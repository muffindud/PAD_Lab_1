from app import app, sock


game_lobby_url = app.config['GAME_LOBBY_HOST'] + ':' + app.config['GAME_LOBBY_PORT']


@sock.route('/connect/<int:id>')
def connect(ws, id):
    # TODO: Redirect to game lobby
    ws.send("Connected to " + str(id))
    while True:
        ws.send("Received: " + ws.receive())
