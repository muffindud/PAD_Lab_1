from app import app
from httpx import AsyncClient
from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads


exchange_service_url = app.config['EXCHANGE_SERVICE_HOST'] + ':' + app.config['EXCHANGE_SERVICE_PORT']


@app.route('/exchange-rate', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def exchange():
    if request.method == 'GET':
        async with AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method='GET',
                url=f'http://{exchange_service_url}/exchange-rate/?baseCurrency={request.args.get("baseCurrency")}&targetCurrency={request.args.get("targetCurrency")}'
            )

        return jsonify(loads(response.text)), response.status_code

    else:
        return jsonify({'error': 'Method not allowed'}), 405
