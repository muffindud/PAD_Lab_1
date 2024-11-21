from app import app, get_service_registry
from src.request_handler import handle_request, NoServiceError, ServiceError

from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads
from pybreaker import CircuitBreaker, CircuitBreakerError


user_manager_breaker = CircuitBreaker(fail_max=app.config['FAIL_MAX'], reset_timeout=app.config['RESET_TIMEOUT'])
service_name = 'User Manager'


round_robin_index = 0
def get_round_robin_user_manager() -> str:
    global round_robin_index
    service_registry = get_service_registry(service_name)

    # If there are no user manager services, return None
    if len(service_registry) == 0:
        return None

    # If the round robin index is out of bounds, reset it
    if round_robin_index >= len(service_registry):
        round_robin_index = 0

    serv_id = list(service_registry.keys())[round_robin_index]

    # Get the next user manager service host
    host = service_registry[serv_id]

    # Increment the round robin index and keep it within bounds
    round_robin_index = (round_robin_index + 1) % len(service_registry)

    return host


@app.route('/register', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def register():
    app.events_counter.inc({'path': '/register'})
    try:
        response = await user_manager_breaker.call_async(
            func=handle_request,
            path=f'/register',
            method='POST',
            host_get=get_round_robin_user_manager,
            service_name=service_name,
            data=await request.get_json(),
        )
        return jsonify(loads(response.text)), response.status_code

    except NoServiceError:
        return jsonify({'error': f'No {service_name} services available'}), 503

    except ServiceError:
        return jsonify({'error': f'Failed to handle request on {service_name} services.'}), 503

    except CircuitBreakerError:
        return jsonify({'error': f'{service_name} service is unavailable'}), 503

    except Exception as e:
        print(f'Failed to handle request: {e}')
        return jsonify({'error': f'Failed to handle request: {e}'}), 503


@app.route('/login', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def login():
    app.events_counter.inc({'path': '/login'})
    try:
        response = await user_manager_breaker.call_async(
            func=handle_request,
            path=f'/login',
            method='GET',
            host_get=get_round_robin_user_manager,
            service_name=service_name,
            data=await request.get_json()
        )
        return jsonify(loads(response.text)), response.status_code

    except NoServiceError:
        return jsonify({'error': f'No {service_name} services available'}), 503

    except ServiceError:
        return jsonify({'error': f'Failed to handle request on {service_name} services.'}), 503

    except CircuitBreakerError:
        return jsonify({'error': f'{service_name} circuit breaker open'}), 503

    except Exception as e:
        print(f'Failed to handle request: {e}')
        return jsonify({'error': f'Failed to handle request: {e}'}), 503



@app.route('/profile', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def profile():
    app.events_counter.inc({'path': '/profile'})
    try:
        response = await user_manager_breaker.call_async(
            func=handle_request,
            path=f'/profile',
            method='GET',
            host_get=get_round_robin_user_manager,
            service_name=service_name,
            headers={'Authorization': request.headers['Authorization']},
            data=await request.get_json()
        )
        return jsonify(loads(response.text)), response.status_code

    except NoServiceError:
        return jsonify({'error': f'No {service_name} services available'}), 503

    except ServiceError:
        return jsonify({'error': f'Failed to handle request on {service_name} services.'}), 503

    except CircuitBreakerError:
        return jsonify({'error': f'{service_name} circuit breaker open'}), 503

    except Exception as e:
        print(f'Failed to handle request: {e}')
        return jsonify({'error': f'Failed to handle request: {e}'}), 503



@app.route('/transfer', methods=['POST'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def transfer():
    app.events_counter.inc({'path': '/transfer'})
    try:
        response = await user_manager_breaker.call_async(
            func=handle_request,
            path=f'/transfer',
            method='POST',
            host_get=get_round_robin_user_manager,
            service_name=service_name,
            headers={'Authorization': request.headers['Authorization']},
            data=await request.get_json()
        )
        return jsonify(loads(response.text)), response.status_code

    except NoServiceError:
        return jsonify({'error': f'No {service_name} services available'}), 503

    except ServiceError:
        return jsonify({'error': f'Failed to handle request on {service_name} services.'}), 503

    except CircuitBreakerError:
        return jsonify({'error': f'{service_name} circuit breaker open'}), 503

    except Exception as e:
        print(f'Failed to handle request: {e}')
        return jsonify({'error': f'Failed to handle request: {e}'}), 503


@app.route('/transfer', methods=['GET'])
@rate_limit(app.config['RATE_LIMIT'], app.config['RATE_LIMIT_PERIOD'])
async def get_transfers():
    app.events_counter.inc({'path': '/transfer'})
    try:
        response = await user_manager_breaker.call_async(
            func=handle_request,
            path=f'/transfer',
            method='GET',
            host_get=get_round_robin_user_manager,
            service_name=service_name,
            headers={'Authorization': request.headers['Authorization']}
        )
        return jsonify(loads(response.text)), response.status_code

    except NoServiceError:
        return jsonify({'error': f'No {service_name} services available'}), 503

    except ServiceError:
        return jsonify({'error': f'Failed to handle request on {service_name} services.'}), 503

    except CircuitBreakerError:
        return jsonify({'error': f'{service_name} circuit breaker open'}), 503

    except Exception as e:
        print(f'Failed to handle request: {e}')
        return jsonify({'error': f'Failed to handle request: {e}'}), 503
