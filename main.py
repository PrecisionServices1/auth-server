from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta
import uuid
import os

app = Flask(__name__)

# Absolute path to keys.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(BASE_DIR, "keys.json")

def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("❌ Error loading keys:", e)
        return []

def save_keys(keys):
    try:
        with open(KEYS_FILE, "w") as f:
            json.dump(keys, f, indent=2)
    except Exception as e:
        print("❌ Error saving keys:", e)

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
        if found["type"] == "day" and datetime.now() > activated_at + timedelta(days=1):
            return jsonify({"status": "expired"}), 403
        elif found["type"] == "week" and datetime.now() > activated_at + timedelta(weeks=1):
            return jsonify({"status": "expired"}), 403

    return jsonify({"status": "valid"}), 200

@app.route("/redeem", methods=["POST"])
def redeem_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")
    print(f"🔑 Redeem request: {key} | HWID: {hwid}")

    found, keys = find_key(key)
    if not found:
        print("❌ Key not found during redeem.")
        return jsonify({"status": "invalid", "reason": "Key not found"}), 404

    if found["activated"]:
        print("⚠️ Key already activated.")
        return jsonify({"status": "already_activated"}), 403

    found["activated"] = True
    found["hwid"] = hwid
    found["activated_at"] = datetime.now().isoformat()

    save_keys(keys)
    print("✅ Key redeemed and saved.")
    return jsonify({"status": "redeemed", "key": key}), 200

@app.route("/addkey", methods=["POST"])
def add_key():
    data = request.json
    new_key = {
        "key": data.get("key"),
        "type": data.get("type"),
        "activated": False,
        "hwid": None,
        "activated_at": None
    }

    keys = load_keys()
    keys.append(new_key)
    save_keys(keys)
    print(f"✅ Key added: {new_key['key']}")
    return jsonify({"status": "added"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
