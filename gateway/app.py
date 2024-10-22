from flask import Flask
from os import environ

app = Flask(__name__)
app.config['USER_MANAGER_HOST'] = environ.get('USER_MANAGER_HOST')
app.config['USER_MANAGER_PORT'] = environ.get('USER_MANAGER_PORT')

import routes.user_manager
