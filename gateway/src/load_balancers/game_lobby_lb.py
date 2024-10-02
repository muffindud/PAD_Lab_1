import itertools
import requests

# will update later
game_lobby_instances = [
    "http://game-lobby-instance-1:5001",
    "http://game-lobby-instance-2:5001",
    "http://game-lobby-instance-3:5001"
]

round_robin = itertools.cycle(game_lobby_instances)


def forward_request_to_game_lobby(endpoint, method="GET", data=None, headers=None):
    """Forward request to the next available Game Lobby instance using round-robin."""
    instance = next(round_robin)
    url = f"{instance}{endpoint}"

    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        return response
    except requests.exceptions.RequestException as e:
        return None
