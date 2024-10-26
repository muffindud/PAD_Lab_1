from httpx import AsyncClient


MAX_RETRIES = 3


async def perform_request(url: str, method: str, headers: dict=None, json: dict=None):
    try:
        async with AsyncClient(timeout=30) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json
            )

        if response.status_code // 100 == 2:
            return response, response.status_code

    except Exception as e:
        return None, 500


async def handle_request(url: str, method: str, headers: dict=None, json: dict=None):
    for _ in range(MAX_RETRIES):
        try:
            response, status_code = await perform_request(url, method, headers, json)
            if status_code // 100 == 2:
                return response.json(), response.status_code

        except Exception as e:
            print(f'No response, trying again...')

    return None, 500
