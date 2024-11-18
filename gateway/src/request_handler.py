from app import app, remove_service

from httpx import AsyncClient, Response


async def handle_request(path: str, method: str, host_get: callable, service_name: str, headers: dict=None, data: dict=None) -> Response:
    try:
        host = host_get()

        if host is None:
            return Response(503, json={'error': f'No {service_name} services available'})

        for i in range(app.config['MAX_RETRIES']):
            async with AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=f"http://{host}{path}",
                    headers=headers,
                    json=data
                )

            if response.status_code < 500:
                return response

        await remove_service(host, service_name)

    except Exception as e:
        print(f'Request failed at {host}: {e}')
