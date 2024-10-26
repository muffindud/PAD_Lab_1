from app import app, get_service_registry
from src.request_form import handle_request

from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads


round_robin_index = 0
def get_round_robin_exchange_service() -> str:
    global round_robin_index
    service_registry = get_service_registry('User Manager')

    # If there are no user manager services, return None
    if len(service_registry) == 0:
        return None

    # If the round robin index is out of bounds, reset it
    if round_robin_index >= len(service_registry):
        round_robin_index = 0

    serv_id = list(service_registry.keys())[round_robin_index]

    # Get the next user manager service host
    host = service_registry[serv_id]

    # Increment the round robin index and keep it within bounds
    round_robin_index = (round_robin_index + 1) % len(service_registry)

    return host


@app.route('/register', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def register():
    host = get_round_robin_exchange_service()
    initial_host = host

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    if request.method == 'POST':
        while True:
            response, status_code = await handle_request(
                f'http://{host}/register',
                request.method,
                json=await request.get_json()
            )

            if status_code // 100 == 2:
                return jsonify(loads(response)), status_code

            print(f'No response, from {host}, trying another service...')
            host = get_round_robin_exchange_service()
            if host == initial_host:
                return jsonify({'error': 'No user manager services available'}), 503

    else:
        return jsonify({'error': 'Invalid request method'}), 400


@app.route('/login', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def login():
    host = get_round_robin_exchange_service()
    initial_host = host

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    if request.method == 'GET':
        while True:
            response, status_code = await handle_request(
                f'http://{host}/login',
                request.method,
                headers={'Authorization': request.headers['Authorization']}
            )

            if status_code // 100 == 2:
                return jsonify(loads(response)), status_code

            print(f'No response, from {host}, trying another service...')
            host = get_round_robin_exchange_service()
            if host == initial_host:
                return jsonify({'error': 'No user manager services available'}), 503

    else:
        return jsonify({'error': 'Invalid request method'}), 400


@app.route('/profile', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def profile():
    host = get_round_robin_exchange_service()
    initial_host = host

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    if request.method == 'GET':
        while True:
            response, status_code = await handle_request(
                f'http://{host}/profile',
                request.method,
                headers={'Authorization': request.headers['Authorization']}
            )

            if status_code // 100 == 2:
                return jsonify(response), status_code

            print(f'No response, from {host}, trying another service...')
            host = get_round_robin_exchange_service()
            if host == initial_host:
                return jsonify({'error': 'No user manager services available'}), 503

    else:
        return jsonify({'error': 'Invalid request method'}), 400


@app.route('/transfer', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def transfer():
    host = get_round_robin_exchange_service()
    initial_host = host

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    if request.method == 'POST':
        while True:
            response, status_code = await handle_request(
                f'http://{host}/transfer',
                request.method,
                headers={'Authorization': request.headers['Authorization']},
                json=await request.get_json()
            )

            if status_code // 100 == 2:
                return jsonify(response), status_code

            print(f'No response, from {host}, trying another service...')
            host = get_round_robin_exchange_service()
            if host == initial_host:
                return jsonify({'error': 'No user manager services available'}), 503

    else:
        return jsonify({'error': 'Invalid request method'}), 400


@app.route('/transfer', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def get_transfers():
    host = get_round_robin_exchange_service()
    initial_host = host

    if host is None:
        return jsonify({'error': 'No user manager services available'}), 503

    if request.method == 'GET':
        while True:
            response, status_code = await handle_request(
                f'http://{host}/transfer',
                request.method,
                headers={'Authorization': request.headers['Authorization']}
            )

            if status_code // 100 == 2:
                return jsonify(response), status_code

            print(f'No response, from {host}, trying another service...')
            host = get_round_robin_exchange_service()
            if host == initial_host:
                return jsonify({'error': 'No user manager services available'}), 503

    else:
        return jsonify({'error': 'Invalid request method'}), 400
