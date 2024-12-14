from app import app, get_service_registry
from src.request_handler import handle_request, NoServiceError, ServiceError
from routes.exchange_service import exchange_service_breaker, get_round_robin_exchange_service

from quart import request, jsonify
from quart_rate_limiter import rate_limit
from json import loads
from pybreaker import CircuitBreaker, CircuitBreakerError
from jwt import decode, encode


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
    task_stack: list[str] = []
    data: dict = await request.get_json()
    source_username: str = decode(request.headers['Authorization'].split(' ')[1], algorithms='HS256', key=app.config['USER_JWT_SECRET'])['username']
    server_token: str = encode({'server': 'Gateway'}, app.config['INTERNAL_JWT_SECRET'], algorithm='HS256')

    try:
        response = await user_manager_breaker.call_async(
            func=handle_request,
            path=f'/transfer',
            method='PUT',
            host_get=get_round_robin_user_manager,
            service_name=service_name,
            headers={'Authorization': f'Bearer {server_token}'},
            data={"amount": -data['amount'], "username": source_username}
        )

        if response.status_code >= 400:
            raise Exception(f'Failed to subtract amount from source user: {response.text}')

        print(f'Subtracted amount from source user: {response.text}')
        task_stack.append('subtract')

        response = await user_manager_breaker.call_async(
            func=handle_request,
            path=f'/transfer',
            method='PUT',
            host_get=get_round_robin_user_manager,
            service_name=service_name,
            headers={'Authorization': f'Bearer {server_token}'},
            data={"amount": data['amount'], "username": data['username']}
        )

        if response.status_code >= 400:
            raise Exception(f'Failed to add amount to destination user: {response.text}')

        print(f'Added amount to destination user: {response.text}')
        task_stack.append('add')

        response = await exchange_service_breaker.call_async(
            func=handle_request,
            path=f'/api/transfer',
            method='POST',
            host_get=get_round_robin_exchange_service,
            service_name=service_name,
            headers={'Authorization': f'Bearer {server_token}'},
            data={"sender": source_username, "receiver": data['username'], "amount": data['amount']}
        )

        if response.status_code >= 400:
            raise Exception(f'Failed to create transfer record: {response.text}')

        print(f'Created transfer record: {response.text}')
        task_stack.append('create_log')

        return jsonify(
            {
                'message': 'Transfer successful',
                'username': data['username'],
                'amount': data['amount']
            }
        ), 200

    except Exception as e:
        print(f'Failed to handle request: {e}, rolling back...')
        while task_stack:
            task = task_stack.pop()
            try:
                if task == 'subtract':
                    response = await user_manager_breaker.call_async(
                        func=handle_request,
                        path=f'/transfer',
                        method='PUT',
                        host_get=get_round_robin_user_manager,
                        service_name=service_name,
                        headers={'Authorization': f'Bearer {server_token}'},
                        data={"amount": data['amount'], "username": source_username}
                    )
                    print(f'Rolling back subtract: {response.text}')

                elif task == 'add':
                    response = await user_manager_breaker.call_async(
                        func=handle_request,
                        path=f'/transfer',
                        method='PUT',
                        host_get=get_round_robin_user_manager,
                        service_name=service_name,
                        headers={'Authorization': f'Bearer {server_token}'},
                        data={"amount": -data['amount'], "username": data['username']}
                    )
                    print(f'Rolling back add: {response.text}')

            except Exception as e:
                print(f'Failed to rollback task {task}: {e}')

        return jsonify({'error': f'Failed to handle request: {e}'}), 500
