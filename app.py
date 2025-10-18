from flask import Flask, request, jsonify
import os
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

UPLOAD_KEY = os.getenv("UPLOAD_KEY", "changeme")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "PH Arbitrage API live",
        "time": datetime.utcnow().isoformat() + "Z"
    })
    return send_from_directory(".", "dashboard.html")

@app.route("/upload", methods=["POST"])
def upload():
    key = request.headers.get("X-API-Key")
    if key != UPLOAD_KEY:
        return jsonify({"error": "unauthorized"}), 403

    content = request.get_json(silent=True)
    if not content or "filename" not in content or "data" not in content:
        return jsonify({"error": "invalid payload"}), 400

    filename = content["filename"]
    filepath = DATA_DIR / filename
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content["data"], f, indent=2)
        print(f"✅ Saved {filename} at {datetime.utcnow().isoformat()}Z")
        return jsonify({"status": "success", "filename": filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/list", methods=["GET"])
def list_files():
    files = [f.name for f in DATA_DIR.glob("*.json")]
    return jsonify({"files": files})

@app.route("/data/<path:filename>", methods=["GET"])
def get_data(filename):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return jsonify({"error": "file not found"}), 404
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
