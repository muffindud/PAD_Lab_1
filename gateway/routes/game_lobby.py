from app import app, sock
from websocket import create_connection
from flask_sock import Server
from flask import request


game_lobby_url = app.config['GAME_LOBBY_HOST'] + ':' + app.config['GAME_LOBBY_PORT']


@sock.route('/connect/<int:id>')
def connect(client_sock: Server, id):
    lobby_sock = create_connection(
        f'ws://{game_lobby_url}/connect/{id}',
        header={'Authorization': request.headers.get('Authorization')}
    )

    while True:
        message = client_sock.receive()
        print(f'Client {id} sent: {message}')
        lobby_sock.send(message)
        response = lobby_sock.recv()
        print(f'Lobby sent: {response}')
        client_sock.send(response)

    lobby_sock.close()
