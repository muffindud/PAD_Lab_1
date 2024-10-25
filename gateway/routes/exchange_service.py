from app import app, get_service_registry
from httpx import AsyncClient
from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads


round_robin_index = 0
def get_round_robin_exchange_service() -> str:
    global round_robin_index
    service_registry = get_service_registry('Exchange Service')

    # If there are no exchange services, return None
    if len(service_registry) == 0:
        return None

    # If the round robin index is out of bounds, reset it
    if round_robin_index >= len(service_registry):
        round_robin_index = 0

    serv_id = list(service_registry.keys())[round_robin_index]

    # Get the next exchange service host
    host = service_registry[serv_id]

    # Increment the round robin index and keep it within bounds
    round_robin_index = (round_robin_index + 1) % len(service_registry)

    return host


@app.route('/exchange-rate', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def exchange():
    host = get_round_robin_exchange_service()

    if host is None:
        return jsonify({'error': 'No exchange services available'}), 503

    if request.method == 'GET':
        async with AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method='GET',
                url=f'http://{host}/exchange-rate/?baseCurrency={request.args.get("baseCurrency")}&targetCurrency={request.args.get("targetCurrency")}'
            )

        try:
            r = jsonify(loads(response.text)), response.status_code
        except Exception as e:
            r = response.text, response.status_code

        return r

    else:
        return jsonify({'error': 'Method not allowed'}), 405
