from app import app, services, data_lock, cache_keys, cache_keys_lock

from flask import request, jsonify
from hashlib import sha256
from bisect import bisect_right
from threading import Lock


SERVICE_NAME = 'Cache'


def hash(value: str) -> int:
    return int(sha256(f'{value}'.encode('utf-8')).hexdigest(), 16)


@app.route('/cache', methods=['GET', 'POST'])
def register_cache():
    if request.method == 'GET':
        healthy_caches = {}

        with data_lock:
            caches = services.get(SERVICE_NAME, {'services': {}})

        for cache_id in caches['services']:
            if caches['services'][cache_id]['status'] == 'healthy':
                healthy_caches[cache_id] = caches['services'][cache_id]['host']

        return jsonify(healthy_caches)

    elif request.method == 'POST':
        data = request.json
        host = data.get('host')
        port = data.get('port')

        cache_id = hash(f'{host}:{port}')

        with data_lock:
            services[SERVICE_NAME] = services.get(SERVICE_NAME, {'services': {}})
            services[SERVICE_NAME]['services'][cache_id] = {
                'host': f'{host}:{port}',
                'status': 'healthy',
                'retry_count': 0,
                'checking': False
            }

        with cache_keys_lock:
            cache_keys.append(cache_id)
            cache_keys.sort()

        return jsonify({
            'message': 'Cache registered successfully',
            'cache_id': cache_id
        })

    else:
        return jsonify({
            'message': 'Invalid request'
        })
