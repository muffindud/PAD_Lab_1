from flask import Blueprint, request, jsonify
from load_balancers.game_lobby_lb import forward_request_to_game_lobby

bp = Blueprint('game_lobby', __name__)


@bp.route('/join', methods=['POST'])
def join_game():
    """Join a game in the Game Lobby."""
    headers = {"Authorization": request.headers.get('Authorization')}
    data = request.get_json()

    if not headers["Authorization"]:
        return jsonify({"message": "Unauthorized"}), 401

    response = forward_request_to_game_lobby(
        "/join", method="POST", data=data, headers=headers)
    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "Game Lobby service unavailable"}), 503


@bp.route('/bet', methods=['POST'])
def place_bet():
    """Place a bet in the Game Lobby."""
    headers = {"Authorization": request.headers.get('Authorization')}
    data = request.get_json()

    if not headers["Authorization"]:
        return jsonify({"message": "Unauthorized"}), 401

    if not isinstance(data.get("amount"), (int, float)):
        return jsonify({"message": "Invalid bet"}), 400

    response = forward_request_to_game_lobby(
        "/bet", method="POST", data=data, headers=headers)
    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "Game Lobby service unavailable"}), 503


@bp.route('/action', methods=['POST'])
def perform_action():
    """Perform an action in the Game Lobby (stand, hit, split, double down)."""
    headers = {"Authorization": request.headers.get('Authorization')}
    data = request.get_json()

    if not headers["Authorization"]:
        return jsonify({"message": "Unauthorized"}), 401

    if data.get("action") not in ["stand", "hit", "split", "double down"]:
        return jsonify({"message": "Invalid action"}), 400

    response = forward_request_to_game_lobby(
        "/action", method="POST", data=data, headers=headers)
    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "Game Lobby service unavailable"}), 503


@bp.route('/leave', methods=['POST'])
def leave_game():
    """Leave the current game in the Game Lobby."""
    headers = {"Authorization": request.headers.get('Authorization')}

    if not headers["Authorization"]:
        return jsonify({"message": "Unauthorized"}), 401

    response = forward_request_to_game_lobby(
        "/leave", method="POST", headers=headers)
    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "Game Lobby service unavailable"}), 503
