from flask import Flask, jsonify, request
import os, json
from datetime import datetime

app = Flask(__name__)

DATA_DIR = "data"
FREE_FILE = os.path.join(DATA_DIR, "free_data.json")
PRO_FILE = os.path.join(DATA_DIR, "pro_data.json")

API_KEY = os.getenv("UPLOAD_KEY", "changeme")

os.makedirs(DATA_DIR, exist_ok=True)

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
        "message": "PH Arbitrage API live"
    })

@app.route("/upload", methods=["POST"])
def upload():
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"error": "unauthorized"}), 403

    content = request.get_json()
    fname = content.get("filename")
    data = content.get("data")

    if not fname or not data:
        return jsonify({"error": "invalid"}), 400

    with open(os.path.join(DATA_DIR, fname), "w") as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "saved", "file": fname})

@app.route("/free")
def free():
    if os.path.exists(FREE_FILE):
        return jsonify(json.load(open(FREE_FILE)))
    return jsonify({"error": "no data"}), 404

@app.route("/pro")
def pro():
    if os.path.exists(PRO_FILE):
        return jsonify(json.load(open(PRO_FILE)))
    return jsonify({"error": "no data"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
