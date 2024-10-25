import asyncio
from quart import Quart, jsonify
from quart_rate_limiter import RateLimiter, rate_limit
from os import environ
from datetime import timedelta
from httpx import AsyncClient
from socket import gethostname
from threading import Lock
from atexit import register

UPDATE_PERIOD = 15  # seconds

app = Quart(__name__)

rate_limiter = RateLimiter(app)
app.config['RATE_LIMIT'] = 5
app.config['RATE_LIMIT_PERIOD'] = timedelta(seconds=1)

app.config['USER_JWT_SECRET'] = environ['USER_JWT_SECRET']

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
