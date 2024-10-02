from flask import Flask, jsonify, request
# import requests
from routes import game_lobby, user_manager, exchange_service

app = Flask(__name__)

app.register_blueprint(game_lobby.bp)
app.register_blueprint(user_manager.bp)
app.register_blueprint(exchange_service.bp)

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint for checking the health of the gateway."""
    return jsonify({"status": "Gateway running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)