# Trigger Fix Test: 2026-03-12T11:34:41Z
# Trigger Test: 2026-03-12T11:18:42Z
# CI Test: change on 2026-03-12T10:46:41Z
import os
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from google.cloud import firestore

# Use env var if set; fallback to gcloud default credentials
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

app = Flask(__name__)
db = firestore.Client(project=PROJECT_ID) if PROJECT_ID else firestore.Client()

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.get("/notes")
def get_notes():
    docs = db.collection("notes").stream()
    items = []
    for d in docs:
        doc = d.to_dict()
        doc["id"] = d.id
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
        ref = db.collection("notes").add(doc)[1]
        doc["id"] = ref.id
        return jsonify(doc), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For local dev
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
# Deploy Fix Test Thu Mar 12 12:22:19 UTC 2026
