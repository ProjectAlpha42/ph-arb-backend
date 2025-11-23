import os
import json
from flask import Flask, request, jsonify, send_from_directory

# Get upload key from environment (Render → Environment variables)
UPLOAD_KEY = os.environ.get("UPLOAD_KEY")

# Base directory of this file (where we keep dashboard.html + JSON files)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


# ---------- Dashboard ----------

@app.route("/")
def dashboard():
    """
    Serve the dashboard HTML file.
    dashboard.html must sit in the same folder as app.py
    """
    return send_from_directory(BASE_DIR, "dashboard.html")


# ---------- JSON endpoints for the dashboard ----------

@app.route("/free_data.json")
def free_data_file():
    """
    Serve free_data.json so the dashboard JS can fetch it.
    """
    path = os.path.join(BASE_DIR, "free_data.json")
    if not os.path.exists(path):
        return jsonify({"error": "free_data.json not found"}), 404

    return send_from_directory(BASE_DIR, "free_data.json", mimetype="application/json")


@app.route("/pro_data.json")
def pro_data_file():
    """
    Serve pro_data.json so the dashboard JS can fetch it.
    """
    path = os.path.join(BASE_DIR, "pro_data.json")
    if not os.path.exists(path):
        return jsonify({"error": "pro_data.json not found"}), 404

    return send_from_directory(BASE_DIR, "pro_data.json", mimetype="application/json")


# ---------- Upload endpoint (from your Pi auto_uploader.py) ----------

@app.route("/upload", methods=["POST"])
def upload():
    """
    Pi posts JSON with header X-Upload-Key and field "tier": "free" or "pro".

    Example JSON from Pi:
    {
        "tier": "free",
        "source": "Binance P2P",
        "buy_price_php": 123.456,
        "sell_price_php": 124.567,
        "official_usd_php": 58.172,
        "buy_spread_pct": 0.436,
        "sell_spread_pct": 0.209,
        "timestamp_utc": "2025-10-18T03:37:47Z"
    }
    """
    if not UPLOAD_KEY:
        return jsonify({"error": "UPLOAD_KEY not configured on server"}), 500

    provided_key = request.headers.get("X-Upload-Key")
    if not provided_key or provided_key != UPLOAD_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "No JSON payload"}), 400

    tier = payload.get("tier", "free")
    if tier not in ("free", "pro"):
        return jsonify({"error": "Invalid tier; must be 'free' or 'pro'"}), 400

    filename = "free_data.json" if tier == "free" else "pro_data.json"
    out_path = os.path.join(BASE_DIR, filename)

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
    except Exception as e:
        return jsonify({"error": f"Failed to write file: {e}"}), 500

    return jsonify({"status": "ok", "tier": tier, "file": filename})


# ---------- Health check (optional, but nice for Render) ----------

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Local dev only; Render will run via gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
