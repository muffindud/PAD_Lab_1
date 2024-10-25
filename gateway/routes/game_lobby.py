from app import app
from websockets import connect as create_connection
from quart import websocket, Websocket, request, jsonify
from quart_rate_limiter import rate_limit
from asyncio import gather
from httpx import AsyncClient
from json import loads


game_lobby_url = app.config['GAME_LOBBY_HOST'] + ':' + app.config['GAME_LOBBY_PORT']


async def client_to_lobby(client_sock: Websocket, lobby_sock):
    try:
        while True:
            client_message = await client_sock.receive()
            await lobby_sock.send(client_message)
    except Exception as e:
        print(f'Error on client forwarding: {e}')
    finally:
        await lobby_sock.close()

async def lobby_to_client(client_sock: Websocket, lobby_sock):
    try:
        while True:
            err_code = 200
            lobby_message = await lobby_sock.recv()
            await client_sock.send(lobby_message)
    except Exception as e:
        print(f'Error on lobby forwarding: {e}')
        err_code = 500
    finally:
        await client_sock.close(err_code)


@app.websocket('/connect/<int:id>')
async def connect(id):
    auth_header = websocket.headers.get('Authorization')

    try:
        lobby_sock = await create_connection(
            f'ws://{game_lobby_url}/connect/{id}',
            extra_headers={'Authorization': auth_header}
        )
    except Exception as e:
        print(f'Error on WS connection: {e}')
        await websocket.close(500)

    await gather(
        client_to_lobby(websocket, lobby_sock),
        lobby_to_client(websocket, lobby_sock)
    )


@app.route('/logs', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def logs():
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='GET',
            url=f'http://{game_lobby_url}/logs',
            headers={'Authorization': request.headers['Authorization']}
        )

    return jsonify(loads(response.text)), response.status_code
