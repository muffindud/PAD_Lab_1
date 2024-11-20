from app import app, get_service_registry
from src.request_handler import handle_request, NoServiceError, ServiceError

from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads
from pybreaker import CircuitBreaker, CircuitBreakerError


exchange_service_breaker = CircuitBreaker(fail_max=app.config['FAIL_MAX'], reset_timeout=app.config['RESET_TIMEOUT'])
service_name = 'Exchange Service'

round_robin_index = 0
def get_round_robin_exchange_service() -> str:
    global round_robin_index
    service_registry = get_service_registry(service_name)

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


# @app.route('/exchange-rate', methods=['GET'])
# @rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
# async def exchange():
#     host = get_round_robin_exchange_service()

#     if host is None:
#         return jsonify({'error': 'No exchange services available'}), 503

#     if request.method == 'GET':
#         async with AsyncClient(timeout=30.0) as client:
#             response = await client.request(
#                 method='GET',
#                 url=f'http://{host}/api/exchange-rate/?baseCurrency={request.args.get("baseCurrency")}&targetCurrency={request.args.get("targetCurrency")}'
#             )

#         try:
#             r = jsonify(loads(response.text)), response.status_code
#         except Exception as e:
#             r = response.text, response.status_code

#         return r

#     else:
#         return jsonify({'error': 'Method not allowed'}), 405


@app.route('/exchange-rate', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def exchange():
    if request.method == 'GET':
        try:
            response = await exchange_service_breaker.call_async(
                func=handle_request,
                path=f'/api/exchange-rate/?baseCurrency={request.args.get("baseCurrency")}&targetCurrency={request.args.get("targetCurrency")}',
                method='GET',
                host_get=get_round_robin_exchange_service,
                service_name=service_name
            )
            # response = await handle_request(
            #     path=f'/api/exchange-rate/?baseCurrency={request.args.get("baseCurrency")}&targetCurrency={request.args.get("targetCurrency")}',
            #     method='GET',
            #     host_get=get_round_robin_exchange_service,
            #     service_name=service_name
            # )
            return jsonify(loads(response.text)), response.status_code

        except NoServiceError:
            return jsonify({'error': f'No {service_name} services available'}), 503

        except ServiceError:
            return jsonify({'error': f'Failed to handle request on {service_name} services'}), 503

        except CircuitBreakerError:
            return jsonify({'error': f'{service_name} circuit breaker open'}), 503

        except Exception as e:
            print(f'Failed to handle request: {e}')
            return jsonify({'error': f'Failed to handle request: {e}'}), 503

    else:
        return jsonify({'error': 'Method not allowed'}), 405
