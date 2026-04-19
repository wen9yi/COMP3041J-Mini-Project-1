import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from database import db, EventRecord

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for all routes
CORS(app)

# Configure database connection (default to SQLite if not provided)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///events.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database with Flask app
db.init_app(app)

# Create database tables if they do not exist
with app.app_context():
    db.create_all()


def record_to_dict(record):
    """
    Convert a database record object into a dictionary format
    for JSON serialization.
    """
    return {
        "id": record.id,
        "title": record.title,
        "description": record.description,
        "location": record.location,
        "date": record.date,
        "organiser": record.organiser,
        "status": record.status,
        "category": record.category,
        "priority": record.priority,
        "note": record.note,
    }


@app.route("/", methods=["GET"])
def home():
    """
    Root endpoint providing basic API information and available routes.
    """
    return jsonify({
        "message": "Campus Buzz Data Service API",
        "version": "1.0",
        "endpoints": {
            "POST /records": "Create a new event record",
            "GET /records": "List all event records",
            "GET /records/<id>": "Retrieve a specific event record",
            "PATCH /records/<id>": "Update status/category/priority/note"
        }
    })


@app.route("/records", methods=["POST"])
def create_record():
    """
    Create a new event record.
    Accepts flexible input; validation and completeness checks
    are expected to be handled by a separate processing function.
    """
    payload = request.get_json(force=True)

    # Create a new EventRecord instance using request payload
    record = EventRecord(
        title=payload.get("title"),
        description=payload.get("description"),
        location=payload.get("location"),
        date=payload.get("date"),
        organiser=payload.get("organiser"),
        status=payload.get("status", "PENDING"),  # Default status
        category=payload.get("category"),
        priority=payload.get("priority"),
        note=payload.get("note"),
    )

    # Save the record to the database
    db.session.add(record)
    db.session.commit()

    return jsonify(record_to_dict(record)), 201


@app.route("/records", methods=["GET"])
def list_records():
    """
    Retrieve all event records from the database.
    """
    records = EventRecord.query.all()
    return jsonify([record_to_dict(record) for record in records])


@app.route("/records/<int:record_id>", methods=["GET"])
def get_record(record_id):
    """
    Retrieve a specific event record by its ID.
    Returns 404 if the record does not exist.
    """
    record = EventRecord.query.get(record_id)
    if record is None:
        return jsonify({"error": "Record not found"}), 404
    return jsonify(record_to_dict(record))


@app.route("/records/<int:record_id>", methods=["PATCH"])
def update_record(record_id):
    """
    Update specific fields of an existing record.
    Supports partial updates (PATCH).

    Accepts both raw field names and processed field names
    (e.g., 'status' or 'final_status').
    """
    payload = request.get_json(force=True)

    # Find the record by ID
    record = EventRecord.query.get(record_id)
    if record is None:
        return jsonify({"error": "Record not found"}), 404

    # Update fields conditionally if present in payload
    if 'status' in payload or 'final_status' in payload:
        record.status = payload.get('status') or payload.get('final_status')

    if 'category' in payload or 'assigned_category' in payload:
        record.category = payload.get('category') or payload.get('assigned_category')

    if 'priority' in payload or 'assigned_priority' in payload:
        record.priority = payload.get('priority') or payload.get('assigned_priority')

    if 'note' in payload:
        record.note = payload['note']

    # Commit changes to the database
    db.session.commit()

    return jsonify(record_to_dict(record))


if __name__ == "__main__":
    """
    Entry point for running the Flask application.
    Accessible externally via port 5002.
    """
    app.run(host="0.0.0.0", port=5002)