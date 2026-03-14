import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import firestore

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
db = firestore.Client(project=PROJECT_ID) if PROJECT_ID else firestore.Client()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.get("/notes")
def get_notes():
    items = []
    for snap in db.collection("notes").stream():
        doc = snap.to_dict()
        doc["id"] = snap.id
        items.append(doc)
    return jsonify(items), 200

@app.post("/notes")
def create_note():
    try:
        payload = request.get_json(force=True) or {}
        message = payload.get("message")
        version = payload.get("version", "v1")
        if not message:
            return jsonify({"error": "message is required"}), 400

        doc = {
            "message": message,
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        }
        _, ref = db.collection("notes").add(doc)
        doc["id"] = ref.id
        return jsonify(doc), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
