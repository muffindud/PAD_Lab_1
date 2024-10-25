from app import app
from flask import request, jsonify

"""
Example:
    {
        "Game Lobby": {
            "gl1": {
                "url": "http://game_lobby-1:8000",
                "status": "healthy"
            },
            "gl2": {
                "url": "http://game_lobby-2:8000",
                "status": "healthy"
            },
            "gl3": {
                "url": "http://game_lobby-3:8000",
                "status": "inactive"
            }
        },
        "User Manager": {
            "um1": {
                "url": "http://user_manager-1:3000",
                "status": "healthy"
            },
            "um2": {
                "url": "http://user_manager-2:3000",
                "status": "inactive"
            }
        },
        "Exchange Service": {
            "es1": {
                "url": "http://exchange_service-1:5000",
                "status": "healthy"
            }
        }
    }
"""
services: dict = {}


@app.route('/dicovery', methods=['GET', 'POST'])
def discovery():
    if request.method == 'GET':
        healthy_services = {}
        for service_name in services:
            healthy_services[service_name] = {}
            for service_id in services[service_name]:
                if services[service_name][service_id]['status'] == 'healthy':
                    healthy_services[service_name][service_id] = services[service_name][service_id]['url']
        return jsonify(healthy_services)

    if request.method == 'POST':
        data = request.json

        service_name = data.get('service_name')
        host = data.get('host')
        port = data.get('port')

        service_id = ""
        for s in service_name.split(" "):
            service_id += s[0].lower()
        service_id += str(len(services.get(service_name, {})) + 1)

        services[service_name] = {
            service_id: {
                'url': f'http://{host}:{port}',
                'status': 'healthy'
            }
        }

        return jsonify({'message': 'Service added successfully', 'service_id': service_id}), 201

    else:
        return jsonify({
            'message': 'Invalid request'
        })


@app.route('/dicovery/<str:service_id>', methods=['GET', 'DELETE'])
def discovery_delete(service_id: str):
    if request.method == 'GET':
        for service_name in services:
            if service_id in services[service_name]:
                return jsonify(services[service_name][service_id])
        return jsonify({
            'message': 'Service not found'
        }), 404

    if request.method == 'DELETE':
        for service_name in services:
            if service_id in services[service_name]:
                services[service_name][service_id]['status'] = 'inactive'
            return jsonify({
                'message': f'Service {service_id} set to inactive'
            })
        return jsonify({
            'message': 'Service not found'
        }), 404

    else:
        return jsonify({
            'message': 'Invalid request'
        })
