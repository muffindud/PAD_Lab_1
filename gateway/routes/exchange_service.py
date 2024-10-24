from app import app
from httpx import AsyncClient
from quart import request, jsonify
from json import loads


exchange_service_url = app.config['EXCHANGE_SERVICE_HOST'] + ':' + app.config['EXCHANGE_SERVICE_PORT']


@app.route('/exchange', methods=['POST'])
async def exchange():
    baseCurrency = request.args.get('baseCurrency')
    targetCurrency = request.args.get('targetCurrency')
    async with AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method='POST',
            url=f'http://{exchange_service_url}/exchange',
            json={'baseCurrency': baseCurrency, 'targetCurrency': targetCurrency}
        )

    return jsonify(loads(response.text)), response.status_code
