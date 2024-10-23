from app import app
from httpx import AsyncClient
from quart import request


user_manager_url = app.config['USER_MANAGER_HOST'] + ':' + app.config['USER_MANAGER_PORT']


@app.route('/register', methods=['POST'])
async def register():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='POST',
            url=f'http://{user_manager_url}/register',
            json=await request.get_json()
        )

    return response.text, response.status_code


@app.route('/login', methods=['GET'])
async def login():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{user_manager_url}/login',
            json=await request.get_json()
        )

    return response.text, response.status_code


@app.route('/profile', methods=['GET'])
async def profile():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{user_manager_url}/profile',
            headers={'Authorization': request.headers['Authorization']}
        )

    return response.text, response.status_code


@app.route('/transfer', methods=['POST'])
async def transfer():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='POST',
            url=f'http://{user_manager_url}/transfer',
            headers={'Authorization': request.headers['Authorization']},
            json=await request.get_json()
        )

    return response.text, response.status_code
