import requests
import os

def handler(event, context):
    record_id = event['id']
    DATA_SERVICE = os.getenv("DATA_SERVICE_URL", "http://localhost:5002")

    # Fill in the results calculated by the Processor [cite: 28, 40]
    payload = {
        "status": event.get('status') or event.get('final_status'),
        "category": event.get('category') or event.get('assigned_category'),
        "priority": event.get('priority') or event.get('assigned_priority'),
        "note": event.get('note')
    }
    requests.patch(f"{DATA_SERVICE}/records/{record_id}", json=payload)
    return {"status": "success"}