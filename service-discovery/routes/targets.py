from app import app, services
from flask import request, jsonify


def get_target(target: str, service: str):
    response = [
        {
            "targets": [],
            "labels": {
                "job": target
            }
        }
    ]

    for service_id in services[service]['services']:
        response[0]['targets'].append(services[service]['services'][service_id]['host'])

    return jsonify(response)


@app.route('/target/game-lobby', methods=['GET'])
def get_game_lobby():
    target = 'game-lobby'
    service = 'Game Lobby'

    return get_target(target, service)


@app.route('/target/user-manager', methods=['GET'])
def get_user_manager():
    target = 'user-manager'
    service = 'User Manager'

    return get_target(target, service)


@app.route('/target/exchange-service', methods=['GET'])
def get_exchange():
    target = 'exchange-service'
    service = 'Exchange Service'

    return get_target(target, service)
