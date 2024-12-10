from quart import Quart, request, jsonify
from datetime import datetime
from asyncio import create_task, sleep
from httpx import AsyncClient
from socket import gethostname
from os import environ
from threading import Lock
from hashlib import sha256
from bisect import bisect_right


RATE_LIFETIME = 60 * 60  # 1 hour
CACHE_RING_UPDATE_INTERVAL = 60 * 1 # 1 minute
SERIVCE_DISCOVERY_URL = f"http:/{environ["SERVICE_DISCOVERY_HOST"]}:{environ["SERVICE_DISCOVERY_PORT"]}/cache"
PORT = environ["QUART_RUN_PORT"]

app = Quart(__name__)

"""
exchange_rates = {
    "USD": {
        "EUR": 0.85,
        "GBP": 0.75,
        ...
        "last_updated": timestamp
    },
    "EUR": {
        "USD": 1.18,
        "GBP": 0.89,
        ...
        "last_updated": timestamp
    },
    ...
}
"""
exchange_rates = {}
ring_updater_task = None

cache_id = None
cache_ring = {}
cache_ring_lock = Lock()
cache_ids = []
cache_ids_lock = Lock()


async def recalibrate_ring(new_cache_ring):
    global cache_ring
    global cache_ring_lock
    global cache_ids
    global cache_ids_lock

    old_ring = None
    old_ids = None

    async with cache_ring_lock:
        old_ring = cache_ring
        cache_ring = {int(cache_id, 16): cache_info for cache_id, cache_info in new_cache_ring.items()}

    async with cache_ids_lock:
        old_ids = cache_ids
        cache_ids = list([int(cache_id, 16) for cache_id in cache_ring.keys()])
        cache_ids.sort()

    # Handle removed nodes (check if the held data is from a lower cache_id)
    # TODO

    # Handle new nodes
    # TODO



async def update_ring():
    global cache_ring
    global cache_ring_lock

    sleep(5)

    while True:
        async with AsyncClient() as client:
            response = await client.get(SERIVCE_DISCOVERY_URL)
            new_cache_ring = response.json()
            if new_cache_ring != cache_ring:
                await recalibrate_ring(new_cache_ring)

        await sleep(CACHE_RING_UPDATE_INTERVAL)


@app.before_serving
async def startup():
    async with AsyncClient() as client:
        response = await client.post(
            SERIVCE_DISCOVERY_URL,
            json={
                "host": gethostname(),
                "port": PORT
            })

        global cache_id
        cache_id = int(response.json()["cache_id"], 16)

    global ring_updater_task
    ring_updater_task = create_task(update_ring())


@app.route('/', methods=['GET'])
async def get_currency():
    try:
        baseCurrency = request.args.get('baseCurrency').lower()
        targetCurrency = request.args.get('targetCurrency').lower()
    except:
        return jsonify(
            {
                "error": "Both baseCurrency and targetCurrency are required."
            }
        ), 400

    if baseCurrency not in exchange_rates:
        return jsonify(
            {
                "error": "Currency not found.",
                "currency": baseCurrency,
                "type": "base"
            }
        ), 404

    # If it works how it should... we should never get here, but just in case
    if targetCurrency not in exchange_rates[baseCurrency]:
        return jsonify(
            {
                "error": "Currency not found.",
                "currency": targetCurrency,
                "type": "target"
            }
        ), 404

    if datetime.timestamp(datetime.now()) - exchange_rates[baseCurrency]["last_updated"] > RATE_LIFETIME:
        return jsonify(
            {
                "error": "Rate outdated. Please update the rates."
            }
        ), 404

    return jsonify(
        {
            "rate": exchange_rates[baseCurrency][targetCurrency]
        }
    )

@app.route('/', methods=['POST'])
async def post_currency():
    try:
        data = request.get_json()
        for baseCurrency, rates in data.items():
            exchange_rates[baseCurrency.lower()] = {rate.lower(): value for rate, value in rates.items()}
            exchange_rates[baseCurrency.lower()]["last_updated"] = datetime.timestamp(datetime.now())

        return jsonify(
            {
                "message": "Exchange rates updated."
            }
        ), 201
    except:
        return jsonify(
            {
                "error": "Invalid data."
            }
        ), 400


@app.route('/health', methods=['GET'])
async def health():
    return jsonify(
        {
            "status": "healthy"
        }
    )


@app.route('/get_all', methods=['GET'])
def get_all():
    return jsonify(exchange_rates)
