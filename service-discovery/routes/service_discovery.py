from app import app, services
from flask import request, jsonify
from os import environ
from threading import Lock


game_lobby_free_port_lock = Lock()
game_lobby_free_port: int = int(environ['GAME_LOBBY_PORT'])


@app.route('/discovery', methods=['GET', 'POST'])
def discovery():
    # GET the list of healthy services
    if request.method == 'GET':
        healthy_services = {}
        for service_name in services:
            healthy_services[service_name] = {}
            for service_id in services[service_name]['services']:
                if services[service_name]['services'][service_id]['status'] == 'healthy':
                    healthy_services[service_name][service_id] = services[service_name]['services'][service_id]['host']
        return jsonify(healthy_services)

    # POST a new service
    if request.method == 'POST':
        data = request.json

        service_name = data.get('service_name')
        host = data.get('host')
        port = data.get('port')

        # Check if the service_name is already in the services dictionary and create it if it doesn't exist
        services[service_name] = services.get(service_name, {'service_seq': 0, 'services': {}})

        # Create a unique sequential service_id
        # first half of each word in the service_name + the next number in the sequence
        service_id = ""
        for s in service_name.split(" "):
            service_id += s[0:int(len(s) / 2)].lower()
        # service_id += str(int(list(services[service_name]['services'].keys())[-1][-1]) + 1) if len(services[service_name]['services'].keys()) != 0 else '0'
        service_id += str(services[service_name]['service_seq'])
        services[service_name]['service_seq'] += 1

        # Add the service to the services dictionary
        services[service_name]['services'][service_id] = {
            'host': f'{host}:{port}',
            'status': 'healthy',
            'retry_count': 0,
            'checking': False
        }

        # Return the service_id
        return jsonify({'message': 'Service added successfully', 'service_id': service_id}), 201

    else:
        return jsonify({
            'message': 'Invalid request'
        })



@app.route('/discovery/get_lobby_port', methods=['GET'])
def get_lobby_port():
    if request.method == 'GET':
        global game_lobby_free_port
        with game_lobby_free_port_lock:
            port = game_lobby_free_port
            game_lobby_free_port += 1
        return jsonify({'port': port})

    else:
        return jsonify({
            'message': 'Invalid request'
        })


@app.route('/discovery/<string:service_id>', methods=['GET', 'DELETE'])
def discovery_delete(service_id: str):
    # GET one service by service_id
    if request.method == 'GET':
        for service_name in services:
            if service_id in services[service_name]['services']:
                return jsonify(services[service_name]['services'][service_id])
        return jsonify({
            'message': 'Service not found'
        }), 404

    # DELETE a service by service_id
    if request.method == 'DELETE':
        for service_name in services:
            if service_id in services[service_name]['services']:
                # services[service_name]['services'][service_id]['status'] = 'inactive'
                del services[service_name]['services'][service_id]
            return jsonify({
                'message': f'Service {service_id} deleted successfully'
            })
        return jsonify({
            'message': 'Service not found'
        }), 404

    else:
        return jsonify({
            'message': 'Invalid request'
        })
