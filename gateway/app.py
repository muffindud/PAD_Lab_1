from quart import Quart, jsonify
from quart_rate_limiter import RateLimiter, rate_limit
from os import environ
from datetime import timedelta


app = Quart(__name__)

rate_limiter = RateLimiter(app)
app.config['RATE_LIMIT'] = 5
app.config['RATE_LIMIT_PERIOD'] = timedelta(seconds=1)

app.config['USER_MANAGER_HOST'] = environ.get('USER_MANAGER_HOST')
app.config['USER_MANAGER_PORT'] = environ.get('USER_MANAGER_PORT')
app.config['GAME_LOBBY_HOST'] = environ.get('GAME_LOBBY_HOST')
app.config['GAME_LOBBY_PORT'] = environ.get('GAME_LOBBY_PORT')
app.config['EXCHANGE_SERVICE_HOST'] = environ.get('EXCHANGE_SERVICE_HOST')
app.config['EXCHANGE_SERVICE_PORT'] = environ.get('EXCHANGE_SERVICE_PORT')


@app.route('/health', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def health():
    return jsonify({'status': 'healthy'}), 200


import routes.user_manager
import routes.game_lobby
