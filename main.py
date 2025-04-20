from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
KEYS_FILE = "keys.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return []
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def find_key(key):
    keys = load_keys()
    for k in keys:
        if k["key"] == key:
            return k, keys
    return None, keys

@app.route("/addkey", methods=["POST"])
def add_key():
    data = request.json
    new_key = data.get("key")
    key_type = data.get("type")

    if not new_key or not key_type:
        return jsonify({"status": "error", "reason": "Missing key or type"}), 400

    keys = load_keys()
    if any(k["key"] == new_key for k in keys):
        return jsonify({"status": "error", "reason": "Key already exists"}), 409

    keys.append({
        "key": new_key,
        "type": key_type,
        "activated": False,
        "hwid": None,
        "activated_at": None
    })

    save_keys(keys)
    return jsonify({"status": "added", "key": new_key}), 200

@app.route("/redeem", methods=["POST"])
def redeem_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    found, keys = find_key(key)
    if not found:
        return jsonify({"status": "invalid", "reason": "Key not found"}), 404

    if found["activated"]:
        return jsonify({"status": "already_activated"}), 403

    found["activated"] = True
    found["hwid"] = hwid
    found["activated_at"] = datetime.now().isoformat()

    save_keys(keys)
    return jsonify({"status": "redeemed", "key": key}), 200

@app.route("/check", methods=["POST"])
def check_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    found, keys = find_key(key)
    if not found:
        return jsonify({"status": "invalid", "reason": "Key not found"}), 404

    if found["hwid"] != hwid:
        return jsonify({"status": "invalid", "reason": "Key bound to another HWID"}), 403

    if found["type"] in ["day", "week"] and found["activated_at"]:
        activated_at = datetime.fromisoformat(found["activated_at"])
        now = datetime.now()
        if found["type"] == "day" and now > activated_at + timedelta(days=1):
            return jsonify({"status": "expired"}), 403
        elif found["type"] == "week" and now > activated_at + timedelta(weeks=1):
            return jsonify({"status": "expired"}), 403

    return jsonify({"status": "valid"}), 200

# ✅ Fix for Render port binding
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses PORT env variable
    app.run(host="0.0.0.0", port=port)
