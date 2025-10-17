from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Secret API key to verify uploads (you’ll add this as an environment variable later)
SECRET_KEY = os.getenv("UPLOAD_KEY", "changeme")

# Folder to store uploaded data
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "time": datetime.utcnow().isoformat()})

@app.route("/upload", methods=["POST"])
def upload():
    key = request.headers.get("X-API-Key")
    if key != SECRET_KEY:
        return jsonify({"error": "unauthorized"}), 403

    content = request.get_json(force=True)
    filename = content.get("filename")
    data = content.get("data")

    if not filename or data is None:
        return jsonify({"error": "missing fields"}), 400

    # Save file to /data
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return jsonify({"status": "ok", "saved": filename})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
