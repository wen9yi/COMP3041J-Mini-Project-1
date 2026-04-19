from flask import Flask, request, jsonify
import os
import requests
from logic import process_event

app = Flask(__name__)
RESULT_UPDATE_URL = os.getenv('RESULT_UPDATE_URL', 'http://localhost:8082/update')

@app.route('/process', methods=['POST'])
def process():
    payload = request.json or {}
    result = process_event(payload)
    event = {
        'id': payload.get('id'),
        **result
    }

    response = requests.post(RESULT_UPDATE_URL, json=event)
    return jsonify({
        'processed': True,
        'processor': event,
        'result_update': response.json() if response.ok else {'error': response.text},
    }), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
