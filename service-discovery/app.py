from flask import Flask, jsonify
from threading import Thread, Lock, Timer
from atexit import register
from requests import get


# The interval in seconds to check the health of the services
HEALTH_CHECK_INTERVAL_SECONDS = 5


"""
Example:
    {
        "Game Lobby": {
            "gl1": {
                "url": "http://game_lobby-1:8000",
                "status": "healthy"
            },
            "gl2": {
                "url": "http://game_lobby-2:8000",
                "status": "healthy"
            },
            "gl3": {
                "url": "http://game_lobby-3:8000",
                "status": "inactive"
            }
        },
        "User Manager": {
            "um1": {
                "url": "http://user_manager-1:3000",
                "status": "healthy"
            },
            "um2": {
                "url": "http://user_manager-2:3000",
                "status": "inactive"
            }
        },
        "Exchange Service": {
            "es1": {
                "url": "http://exchange_service-1:5000",
                "status": "healthy"
            }
        }
    }
"""
services: dict = {}
data_lock = Lock()
timer = Timer(0, lambda: None, ())


def create_app():
    app = Flask(__name__)

    # Register the interrupt function to stop the health check timer
    def interrupt():
        global timer
        timer.cancel()

    # Check the health of a service
    def check_service(service_name, service_id, url):
        print(f'Checking {service_name} {service_id} at {url}')
        try:
            response = get(url + '/health')
            if response.status_code == 200:
                with data_lock:
                    services[service_name][service_id]['status'] = 'healthy'
                    print(f'{service_name} {service_id} is healthy')

            elif response.status_code == 429:
                with data_lock:
                    services[service_name][service_id]['status'] = 'healthy'
                    print(f'{service_name} {service_id} is healthy, but returned {response.status_code} - Too Many Requests')

            else:
                with data_lock:
                    services[service_name][service_id]['status'] = 'unhealthy'
                    print(f'{service_name} {service_id} is unhealthy status code {response.status_code}')
        except:
            with data_lock:
                services[service_name][service_id]['status'] = 'inactive'
                print(f'{service_name} {service_id} is inactive status code pobably 500')

    # Health check all services in parallel
    def health_check():
        global services
        global timer
        with data_lock:
            threads = []
            for service_name in services:
                for service_id in services[service_name]:
                    url = services[service_name][service_id]['url']
                    thread = Thread(target=check_service, args=(service_name, service_id, url))
                    thread.start()
                    threads.append(thread)

        timer = Timer(HEALTH_CHECK_INTERVAL_SECONDS, health_check, ())
        timer.start()

    # Start the health check timer
    def start_health_check():
        global timer
        timer = Timer(0, health_check, ())
        timer.start()

    start_health_check()
    register(interrupt)

    return app


app = create_app()
import routes.service_discovery
