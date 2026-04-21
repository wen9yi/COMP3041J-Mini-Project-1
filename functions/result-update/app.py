from flask import Flask, request, jsonify
from updater import handler

app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update():
    payload = request.json or {}
    result = handler(payload, None)
    return jsonify(result)

if __name__ == '__main__':
    # Keep this separate from processor (8081) for local dev.
    app.run(host='0.0.0.0', port=8082)
