from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DATA_SERVICE = os.getenv("DATA_SERVICE_URL", "http://localhost:5002")
EVENT_FUNC = os.getenv("SUBMISSION_EVENT_URL", "http://localhost:8080/event")


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Campus Buzz Workflow Service API",
        "version": "1.0",
        "endpoints": {
            "POST /api/submit": "Submit a new event for processing"
        }
    })


@app.route('/api/submit', methods=['POST'])
def handle_submission():
    payload = request.get_json(force=True)
    
    # 允许任何形式的提交，Processing Function 将判定完整性
    # 1. 创建初始记录，状态默认 PENDING
    data_payload = {**payload, "status": "PENDING"}
    data_response = requests.post(f"{DATA_SERVICE}/records", json=data_payload, timeout=5)
    if data_response.status_code != 201:
        return jsonify({
            "error": "Failed to create record in Data Service",
            "details": data_response.json()
        }), 502

    record = data_response.json()

    # 2. 触发 Submission Event Function，模拟异步调用
    event_payload = {"id": record["id"], **payload}
    try:
        requests.post(EVENT_FUNC, json=event_payload, timeout=5)
    except requests.RequestException:
        # 这里我们可以忽略异步触发错误，仍然返回 202 Accepted
        pass

    return jsonify({
        "message": "Submission received",
        "id": record["id"],
        "status": "PENDING"
    }), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
