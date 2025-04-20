from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

KEYS_FILE = "keys.json"

def load_keys():
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

@app.route("/check", methods=["POST"])
def check_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    found, keys = find_key(key)
    if not found:
        return jsonify({"status": "invalid", "reason": "Key not found"}), 404

    if found["activated"] and found["hwid"] != hwid:
        return jsonify({"status": "invalid", "reason": "Key already used on another HWID"}), 403

    if found["activated"]:
        activated_at = datetime.fromisoformat(found["activated_at"])
        if found["type"] == "day":
            if datetime.now() > activated_at + timedelta(days=1):
                return jsonify({"status": "expired"}), 403
        elif found["type"] == "week":
            if datetime.now() > activated_at + timedelta(weeks=1):
                return jsonify({"status": "expired"}), 403

    return jsonify({"status": "valid"}), 200

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
