from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS
from dotenv import load_dotenv
import threading

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for all routes
CORS(app)

# External service endpoints (configurable via environment variables)
DATA_SERVICE = os.getenv("DATA_SERVICE_URL", "http://localhost:5002")
EVENT_FUNC = os.getenv("SUBMISSION_EVENT_URL", "http://localhost:8080/event")


@app.route("/", methods=["GET"])
def home():
    """
    Root endpoint providing API information and available routes.
    """
    return jsonify({
        "message": "Campus Buzz Workflow Service API",
        "version": "1.0",
        "endpoints": {
            "POST /api/submit": "Submit a new event for processing"
        }
    })


@app.route('/api/submit', methods=['POST'])
def handle_submission():
    """
    Handle event submission requests.

    Workflow:
    1. Accept incoming event data (no strict validation at this stage).
    2. Create an initial record in the Data Service with status = PENDING.
    3. Trigger an asynchronous event processing function.
    4. Return a 202 Accepted response to indicate async processing.
    """
    payload = request.get_json(force=True)

    # Step 1: Create initial record with default status "PENDING"
    data_payload = {**payload, "status": "PENDING"}

    data_response = requests.post(
        f"{DATA_SERVICE}/records",
        json=data_payload,
        timeout=5
    )

    # Handle failure when calling Data Service
    if data_response.status_code != 201:
        return jsonify({
            "error": "Failed to create record in Data Service",
            "details": data_response.json()
        }), 502

    # Extract created record information
    record = data_response.json()

    # Step 2: Trigger asynchronous event processing (fire-and-forget)
    event_payload = {"id": record["id"], **payload}

    def trigger():
        try:
            # Keep this short so submit latency stays low.
            requests.post(EVENT_FUNC, json=event_payload, timeout=2)
        except requests.RequestException:
            # Ignore failures in async triggering to avoid blocking client response
            pass

    threading.Thread(target=trigger, daemon=True).start()

    # Step 3: Return acknowledgment (async processing)
    return jsonify({
        "message": "Submission received",
        "id": record["id"],
        "status": "PENDING"
    }), 202


if __name__ == "__main__":
    """
    Entry point for running the Workflow Service.
    Exposes the API on port 5001.
    """
    app.run(host="0.0.0.0", port=5001)