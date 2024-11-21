import asyncio
from quart import Quart, jsonify, request
from quart_rate_limiter import RateLimiter, rate_limit
from os import environ
from datetime import timedelta
from httpx import AsyncClient
from socket import gethostname
from threading import Lock
from atexit import register
from aioprometheus import Counter, MetricsMiddleware
from aioprometheus.asgi.quart import metrics

UPDATE_PERIOD = 15  # seconds

app = Quart(__name__)

app.events_couter = Counter('http_requests_total', 'Total HTTP Requests')

app.asgi_app = MetricsMiddleware(app.asgi_app)
app.add_url_rule('/metrics', 'metrics', metrics, methods=['GET'])

rate_limiter = RateLimiter(app)
app.config['RATE_LIMIT'] = 5
app.config['RATE_LIMIT_PERIOD'] = timedelta(seconds=1)

app.config['MAX_RETRIES'] = 3
app.config['FAIL_MAX'] = 3
app.config['RESET_TIMEOUT'] = 30

app.config['USER_JWT_SECRET'] = environ['USER_JWT_SECRET']
app.config['INTERNAL_JWT_SECRET'] = environ['INTERNAL_JWT_SECRET']

app.config['GAME_LOBBY_HOST'] = environ['GAME_LOBBY_HOST']

service_discovery_url = f'http://{environ["SERVICE_DISCOVERY_HOST"]}:{environ["SERVICE_DISCOVERY_PORT"]}'
service_id = ""

service_registry = {}
service_registry_lock = Lock()
registry_updater_task = None


def get_service_registry(service_name: str=None) -> dict:
    global service_registry
    global service_registry_lock

    with service_registry_lock:
        if service_name:
            return service_registry.get(service_name, {})
        return service_registry


async def remove_service(service_host: str, service_name: str):
    global service_registry
    global service_registry_lock

    s_id = None

    with service_registry_lock:
        for service_id, host in service_registry[service_name].items():
            if host == service_host:
                del service_registry[service_name][service_id]
                s_id = service_id
                break

    if s_id:
        async with AsyncClient(timeout=30.0) as client:
            await client.request(
                method='DELETE',
                url=f'{service_discovery_url}/discovery/{s_id}'
            )


async def get_services():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.get(f'{service_discovery_url}/discovery')
        return response.json()


async def update_registry():
    global service_registry
    global service_registry_lock

    while True:
        print('Updating registry...')
        try:
            services = await get_services()
            with service_registry_lock:
                service_registry = services
            print(f'Updated registry: {service_registry}')
        except Exception as e:
            print(f'Error updating registry: {e}')

        await asyncio.sleep(UPDATE_PERIOD)  # Wait before next update


@app.before_serving
async def startup():
    # Register the service with the service discovery
    async with AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f'{service_discovery_url}/discovery',
            json={
                'service_name': 'Gateway',
                'host': gethostname(),
                'port': environ['QUART_RUN_PORT']
            }
        )

        global service_id
        service_id = response.json()['service_id']
        print(f'Registered Gateway service with ID: {service_id}')

    # Start the registry update loop
    global registry_updater_task
    registry_updater_task = asyncio.create_task(update_registry())


# @app.before_request
# async def before_request():
#     http_request_total.inc({'method': request.method, 'endpoint': request.path, 'status': 'in-progress'})


# @app.after_request
# async def after_request(response):
#     http_request_total.inc({'method': request.method, 'endpoint': request.path, 'status': response.status_code})
#     logger.info(f'{request.method} {request.path} - {response.status_code}')
#     return response


@app.after_serving
async def shutdown():
    # Ensure registry updater task is properly cancelled on shutdown
    global registry_updater_task
    if registry_updater_task:
        registry_updater_task.cancel()
        try:
            await registry_updater_task
        except asyncio.CancelledError:
            print('Registry updater task cancelled.')


@app.route('/health', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def health():
    return jsonify({'status': 'healthy'}), 200


import routes.user_manager
import routes.game_lobby
import routes.exchange_service


register(lambda: None)
