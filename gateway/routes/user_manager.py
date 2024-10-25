from app import app, service_registry
from httpx import AsyncClient
from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads


round_robin_index = 0
def get_round_robin_exchange_service() -> str:
    # If there are no user manager services, return None
    if len(service_registry['User Manager']) == 0:
        return None

    # If the round robin index is out of bounds, reset it
    if round_robin_index >= len(service_registry['User Manager']):
        round_robin_index = 0

    # Get the next user manager service host
    host = service_registry['User Manager'][round_robin_index]

    # Increment the round robin index and keep it within bounds
    round_robin_index = (round_robin_index + 1) % len(service_registry['User Manager'])

    return host


@app.route('/register', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def register():
    host = get_round_robin_exchange_service()

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='POST',
            url=f'http://{host}/register',
            json=await request.get_json()
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/login', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def login():
    host = get_round_robin_exchange_service()

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{host}/login',
            json=await request.get_json()
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/profile', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def profile():
    host = get_round_robin_exchange_service()

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{host}/profile',
            headers={'Authorization': request.headers['Authorization']}
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/transfer', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def transfer():
    host = get_round_robin_exchange_service()

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='POST',
            url=f'http://{host}/transfer',
            headers={'Authorization': request.headers['Authorization']},
            json=await request.get_json()
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/transfer', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def get_transfers():
    host = get_round_robin_exchange_service()

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{host}/transfer',
            headers={'Authorization': request.headers['Authorization']}
        )

    return jsonify(loads(response.text)), response.status_code
