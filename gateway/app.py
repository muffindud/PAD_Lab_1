from flask import Flask
from flask_sock import Sock
from os import environ

app = Flask(__name__)
sock = Sock(app)
app.config['USER_MANAGER_HOST'] = environ.get('USER_MANAGER_HOST')
app.config['USER_MANAGER_PORT'] = environ.get('USER_MANAGER_PORT')
app.config['GAME_LOBBY_HOST'] = environ.get('GAME_LOBBY_HOST')
app.config['GAME_LOBBY_PORT'] = environ.get('GAME_LOBBY_PORT')

import routes.user_manager
import routes.game_lobby
