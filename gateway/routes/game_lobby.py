from app import app, get_service_registry
from websockets import connect as create_connection
from quart import websocket, Websocket, request, jsonify
from quart_rate_limiter import rate_limit
from asyncio import gather
from httpx import AsyncClient
from json import loads
from jwt import decode


round_robin_index = 0
def get_round_robin_game_lobby_service() -> str:
    global round_robin_index
    service_registry = get_service_registry('Game Lobby')

    # If there are no game lobby services, return None
    if len(service_registry) == 0:
        return None

    # If the round robin index is out of bounds, reset it
    if round_robin_index >= len(service_registry):
        round_robin_index = 0

    serv_id = list(service_registry.keys())[round_robin_index]

    # Get the next game lobby service host
    host = service_registry[serv_id]

    # Increment the round robin index and keep it within bounds
    round_robin_index = (round_robin_index + 1) % len(service_registry)

    return host


round_robin_index_ws = 0
def get_round_robin_ws_game_lobby_service() -> str:
    global round_robin_index_ws
    service_registry = get_service_registry('Game Lobby')

    # If there are no game lobby services, return None
    if len(service_registry) == 0:
        return None

    # If the round robin index is out of bounds, reset it
    if round_robin_index_ws >= len(service_registry):
        round_robin_index_ws = 0

    serv_id = list(service_registry.keys())[round_robin_index_ws]

    # Get the next game lobby service host
    host = service_registry[serv_id]

    # Increment the round robin index and keep it within bounds
    round_robin_index_ws = (round_robin_index_ws + 1) % len(service_registry)

    return host


"""
Example: {
    "game_lobby_service_1": {
        1: [Client1, Client2],
        3: [Client3],
        4: [Client5, Client6, Client7],
    },
    "game_lobby_service_2": {
        2: [Client4],
        5: [Client8, Client9],
    }
    ...
}
"""
active_lobbies = {}
def get_lobby_host(lobby_id: int, client: str) -> str:
    for host, lobbies in active_lobbies.items():
        if lobby_id in lobbies.keys():
            lobbies[lobby_id].append(client)
            return host

    h = get_round_robin_ws_game_lobby_service()

    if h:
        active_lobbies[h] = {lobby_id: [client]}

    return h


def user_disconnect(client: str):
    try:
        for host, lobbies in active_lobbies.items():
            for lobby_id, clients in lobbies.items():
                if client in clients:
                    clients.remove(client)
                    if len(clients) == 0:
                        lobbies.pop(lobby_id)
                    return
    except Exception as e:
        print(f'Error on user disconnect: {e}')


async def client_to_lobby(client_sock: Websocket, lobby_sock):
    try:
        while True:
            client_message = await client_sock.receive()
            await lobby_sock.send(client_message)
    except Exception as e:
        print(f'Error on client forwarding: {e}')
    finally:
        user_disconnect(websocket.headers.get('Authorization'))
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
        user_disconnect(websocket.headers.get('Authorization'))
        await client_sock.close(err_code)


@app.websocket('/connect/<int:id>')
async def connect(id):
    auth_header = websocket.headers.get('Authorization')
    # username = decode(auth_header.split(' ')[1], options={"verify_signature": False}, algorithms=['HS256'])['username']

    username = ""
    try:
        username = decode(auth_header.split(' ')[1], algorithms='HS256', key=app.config['USER_JWT_SECRET'])['username']
    except Exception as e:
        print(f'Error decoding JWT: {e}')
        await websocket.close(401)
        return

    host = get_lobby_host(id, username)

    try:
        lobby_sock = await create_connection(
            f'ws://{host}/connect/{id}',
            extra_headers={'Authorization': auth_header}
        )
    except Exception as e:
        print(f'Error on WS connection: {e}')
        user_disconnect(auth_header)
        await websocket.close(500)

    await gather(
        client_to_lobby(websocket, lobby_sock),
        lobby_to_client(websocket, lobby_sock)
    )


@app.route('/logs', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def logs():
    host = get_round_robin_game_lobby_service()
    initial_host = host

    if host is None:
        return jsonify({'error': 'No game lobby services available'}), 503

    if request.method == 'GET':
        while True:
            response, status = await handle_request(
                f'http://{host}/logs',
                request.method
            )

            if response.status_code // 100 == 2:
                return jsonify(loads(response)), status

            print(f'No response, from {host}, trying another service...')
            host = get_round_robin_game_lobby_service()
            if host == initial_host:
                return jsonify({'error': 'No game lobby services available'}), 503

    else:
        return jsonify({'error': 'Invalid request method'}), 400
