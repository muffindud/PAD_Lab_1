from flask import Blueprint, request, jsonify
from load_balancers.user_manager_lb import forward_request_to_user_manager

bp = Blueprint('user_manager', __name__)


@bp.route('/register', methods=['POST'])
def register_user():
    """Create a new user."""
    data = request.get_json()
    response = forward_request_to_user_manager(
        "/register", method="POST", data=data)

    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "User Manager service unavailable"}), 503


@bp.route('/login', methods=['GET'])
def login_user():
    """Log in a user."""
    data = request.get_json()
    response = forward_request_to_user_manager(
        "/login", method="GET", data=data)

    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "User Manager service unavailable"}), 503


@bp.route('/profile', methods=['GET'])
def get_user_profile():
    """Get the user's profile."""
    headers = {"Authorization": request.headers.get('Authorization')}

    if not headers["Authorization"]:
        return jsonify({"message": "Unauthorized"}), 401

    response = forward_request_to_user_manager(
        "/profile", method="GET", headers=headers)

    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "User Manager service unavailable"}), 503


@bp.route('/transfer', methods=['POST'])
def transfer_money():
    """Transfer money between users."""
    headers = {"Authorization": request.headers.get('Authorization')}
    data = request.get_json()

    if not headers["Authorization"]:
        return jsonify({"message": "Unauthorized"}), 401

    response = forward_request_to_user_manager(
        "/transfer", method="POST", data=data, headers=headers)

    if response:
        return jsonify(response.json()), response.status_code
    return jsonify({"message": "User Manager service unavailable"}), 503
