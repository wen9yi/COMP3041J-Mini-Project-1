import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from database import db, EventRecord

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///events.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def record_to_dict(record):
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
    payload = request.get_json(force=True)

    # 允许任何形式的提交，Processing Function 将判定完整性
    record = EventRecord(
        title=payload.get("title"),
        description=payload.get("description"),
        location=payload.get("location"),
        date=payload.get("date"),
        organiser=payload.get("organiser"),
        status=payload.get("status", "PENDING"),
        category=payload.get("category"),
        priority=payload.get("priority"),
        note=payload.get("note"),
    )

    db.session.add(record)
    db.session.commit()

    return jsonify(record_to_dict(record)), 201


@app.route("/records", methods=["GET"])
def list_records():
    records = EventRecord.query.all()
    return jsonify([record_to_dict(record) for record in records])


@app.route("/records", methods=["DELETE"])
def delete_all_records():
    records = EventRecord.query.all()
    for record in records:
        db.session.delete(record)
    db.session.commit()
    return jsonify({"deleted": len(records)})


@app.route("/records/<int:record_id>", methods=["GET"])
def get_record(record_id):
    record = EventRecord.query.get(record_id)
    if record is None:
        return jsonify({"error": "Record not found"}), 404
    return jsonify(record_to_dict(record))


@app.route("/records/<int:record_id>", methods=["PATCH"])
def update_record(record_id):
    payload = request.get_json(force=True)
    record = EventRecord.query.get(record_id)
    if record is None:
        return jsonify({"error": "Record not found"}), 404

    if 'status' in payload or 'final_status' in payload:
        record.status = payload.get('status') or payload.get('final_status')
    if 'category' in payload or 'assigned_category' in payload:
        record.category = payload.get('category') or payload.get('assigned_category')
    if 'priority' in payload or 'assigned_priority' in payload:
        record.priority = payload.get('priority') or payload.get('assigned_priority')
    if 'note' in payload:
        record.note = payload['note']

    db.session.commit()
    return jsonify(record_to_dict(record))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
