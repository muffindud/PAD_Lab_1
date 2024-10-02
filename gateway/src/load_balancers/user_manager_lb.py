import itertools
import requests

# will update later
user_manager_instances = [
    "http://user-manager-instance-1:5002",
    "http://user-manager-instance-2:5002",
    "http://user-manager-instance-3:5002"
]

round_robin = itertools.cycle(user_manager_instances)


def forward_request_to_user_manager(endpoint, method="GET", data=None, headers=None):
    """Forward request to the next available User Manager instance using round-robin."""
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
