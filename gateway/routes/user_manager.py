from app import app
from requests import post, get
from flask import jsonify, request


user_manager_url = app.config['USER_MANAGER_HOST'] + ':' + app.config['USER_MANAGER_PORT']


@app.route('/register', methods=['POST'])
def register():
    response = post(
        url='http://' + user_manager_url + '/register',
        json=request.json
    )

    return response.text, response.status_code


@app.route('/login', methods=['GET'])
def login():
    response = get(
        url='http://' + user_manager_url + '/login',
        json=request.json
    )

    return response.text, response.status_code


@app.route('/profile', methods=['GET'])
def profile():
    response = get(
        url='http://' + user_manager_url + '/profile',
        headers=request.headers
    )

    return response.text, response.status_code


@app.route('/transfer', methods=['POST'])
def transfer():
    response = post(
        url='http://' + user_manager_url + '/transfer',
        json=request.json
    )

    return response.text, response.status_code
