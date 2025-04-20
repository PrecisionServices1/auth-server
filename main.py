from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta

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

@app.route("/addkey", methods=["POST"])
def add_key():
    data = request.json
    new_key = {
        "key": data["key"],
        "type": data["type"],
        "activated": False,
        "hwid": "",
        "activated_at": ""
    }
    keys = load_keys()
    keys.append(new_key)
    save_keys(keys)
    return jsonify({"status": "added"}), 200

@app.route("/redeem", methods=["POST"])
def redeem_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    found, keys = find_key(key)
    if not found:
        return jsonify({"status": "invalid", "reason": "Key not found"}), 404

    if found["activated"]:
        return jsonify({"status": "already_activated", "reason": "Key already redeemed"}), 403

    found["activated"] = True
    found["hwid"] = hwid
    found["activated_at"] = datetime.now().isoformat()
    save_keys(keys)

    return jsonify({"status": "redeemed"}), 200

@app.route("/")
def home():
    return "✅ Auth server is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
