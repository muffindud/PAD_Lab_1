from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# will update urls later
GAME_LOBBY_LB_URL = 'http://localhost:8001/api/game'
USER_MANAGER_LB_URL = 'http://localhost:8002/api/user'


@app.route('/api/game/<path:subpath>', methods=['POST', 'GET'])
def game_lobby(subpath):
    """Forward requests to the Game Lobby Load Balancer."""
    url = f"{GAME_LOBBY_LB_URL}/{subpath}"
    response = requests.request(
        method=request.method, url=url, headers=request.headers, json=request.get_json())
    return jsonify(response.json()), response.status_code


@app.route('/api/user/<path:subpath>', methods=['POST', 'GET'])
def user_manager(subpath):
    """Forward requests to the User Manager Load Balancer."""
    url = f"{USER_MANAGER_LB_URL}/{subpath}"
    response = requests.request(
        method=request.method, url=url, headers=request.headers, json=request.get_json())
    return jsonify(response.json()), response.status_code


@app.route('/status', methods=['GET'])
def status():
    """Status endpoint for checking the health of the gateway."""
    return jsonify({"status": "Gateway running"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
