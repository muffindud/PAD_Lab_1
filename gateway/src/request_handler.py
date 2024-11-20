from app import app, remove_service, get_service_registry

from httpx import AsyncClient, Response, ConnectError

class CircuitBreakerError(Exception):
    pass

class NoServiceError(Exception):
    pass

class ServiceError(Exception):
    pass

async def handle_request(path: str, method: str, host_get: callable, service_name: str, headers: dict=None, data: dict=None) -> Response:
    # try:
    #     host = host_get()

    #     if host is None:
    #         return Response(503, json={'error': f'No {service_name} services available'})

    #     async with AsyncClient(timeout=30.0) as client:
    #         response = await client.request(
    #             method=method,
    #             url=f"http://{host}{path}",
    #             headers=headers,
    #             json=data
    #         )

    #     if response.status_code < 500:
    #         return response

    #     response.raise_for_status()

    # except Exception as e:
    #     print(f'Failed to handle request on {host}: {e}')
    #     # TODO: See if sleeping here is necessary

    # remove_service(host, service_name)
    # raise ConnectError(f'Failed to handle request on {host}')

    initial_host = None
    while True:
        host = host_get()

        if host is None:
            raise NoServiceError(f'No {service_name} services available')

        if host == initial_host:
            raise ServiceError(f'Failed to handle request on {service_name} services.')

        initial_host = host if initial_host is None else initial_host

        for _ in range(app.config['MAX_RETRIES']):
            try:
                async with AsyncClient(timeout=30.0) as client:
                    response = await client.request(
                        method=method,
                        url=f"http://{host}{path}",
                        headers=headers,
                        json=data
                    )

                if response.status_code < 500:
                    return response

                response.raise_for_status()

            except ConnectError as e:
                print(f'Failed to handle request on {host}: {e}')
