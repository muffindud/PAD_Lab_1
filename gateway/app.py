from quart import Quart
from os import environ

app = Quart(__name__)

app.config['USER_MANAGER_HOST'] = environ.get('USER_MANAGER_HOST')
app.config['USER_MANAGER_PORT'] = environ.get('USER_MANAGER_PORT')
app.config['GAME_LOBBY_HOST'] = environ.get('GAME_LOBBY_HOST')
app.config['GAME_LOBBY_PORT'] = environ.get('GAME_LOBBY_PORT')

import routes.user_manager
import routes.game_lobby
