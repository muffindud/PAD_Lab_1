from flask import Flask
from os import environ


app = Flask(__name__)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=environ["PORT"])
