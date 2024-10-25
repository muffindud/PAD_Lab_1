from app import app
from httpx import AsyncClient
from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads


user_manager_url = app.config['USER_MANAGER_HOST'] + ':' + app.config['USER_MANAGER_PORT']


@app.route('/register', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def register():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='POST',
            url=f'http://{user_manager_url}/register',
            json=await request.get_json()
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/login', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def login():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{user_manager_url}/login',
            json=await request.get_json()
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/profile', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def profile():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{user_manager_url}/profile',
            headers={'Authorization': request.headers['Authorization']}
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/transfer', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def transfer():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='POST',
            url=f'http://{user_manager_url}/transfer',
            headers={'Authorization': request.headers['Authorization']},
            json=await request.get_json()
        )

    return jsonify(loads(response.text)), response.status_code


@app.route('/transfer', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def get_transfers():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{user_manager_url}/transfer',
            headers={'Authorization': request.headers['Authorization']}
        )

    return jsonify(loads(response.text)), response.status_code
