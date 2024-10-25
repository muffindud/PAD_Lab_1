from app import app, service_registry
from httpx import AsyncClient
from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads


round_robin_index = 0
def get_round_robin_exchange_service() -> str:
    # If there are no exchange services, return None
    if len(service_registry['Exchange Service']) == 0:
        return None

    # If the round robin index is out of bounds, reset it
    if round_robin_index >= len(service_registry['Exchange Service']):
        round_robin_index = 0

    # Get the next exchange service host
    host = service_registry['Exchange Service'][round_robin_index]

    # Increment the round robin index and keep it within bounds
    round_robin_index = (round_robin_index + 1) % len(service_registry['Exchange Service'])

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

        return jsonify(loads(response.text)), response.status_code

    else:
        return jsonify({'error': 'Method not allowed'}), 405
