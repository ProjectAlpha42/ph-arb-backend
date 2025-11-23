import os
import json
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory, abort

app = Flask(__name__)

# Folder to store uploaded JSON data
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Secret upload key (must match what your Pi uses as X-API-Key)
UPLOAD_KEY = os.getenv("UPLOAD_KEY", "changeme")


# -------------------------
# Public routes
# -------------------------

@app.route("/", methods=["GET"])
def dashboard():
    """
    Public dashboard page.
    For now this is open; later we can add login/paid gating.
    """
    return send_from_directory(".", "dashboard.html")


@app.route("/status", methods=["GET"])
def status():
    """
    Simple JSON status endpoint (good for debugging or uptime checks).
    """
    return jsonify(
        {
            "status": "ok",
            "message": "PH Arbitrage API live",
            "time": datetime.utcnow().isoformat() + "Z",
        }
    )


@app.route("/data/<path:filename>", methods=["GET"])
def get_data(filename):
    """
    Serve stored JSON data (free_data.json, pro_data.json, etc.).
    This is what the dashboard fetches.
    """
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return jsonify({"error": "file not found"}), 404

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/list", methods=["GET"])
def list_files():
    """
    List JSON files currently stored in the data folder.
    """
    files = [p.name for p in DATA_DIR.glob("*.json")]
    return jsonify({"files": files})


# -------------------------
# Private upload endpoint (Pi → backend)
# -------------------------

@app.route("/upload", methods=["POST"])
def upload():
    """
    Pi calls this with X-API-Key and JSON body:
    {
        "filename": "free_data.json" or "pro_data.json",
        "data": { ... }
    }
    """
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


# -------------------------
# Entry point for local dev / gunicorn
# -------------------------

if __name__ == "__main__":
    # For local testing; Render uses gunicorn with app:app
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
