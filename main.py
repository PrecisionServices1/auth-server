@app.route("/check", methods=["POST"])
def check_key():
    try:
        data = request.json
        key = data.get("key")
        hwid = data.get("hwid")

        found, keys = find_key(key)
        if not found:
            return jsonify({"status": "invalid", "reason": "Key not found"}), 404

        if not found["activated"]:
            return jsonify({"status": "invalid", "reason": "Key not activated"}), 403

        if found["hwid"] != hwid:
            return jsonify({"status": "invalid", "reason": "HWID mismatch"}), 403

        if found["type"] == "day":
            activated = datetime.fromisoformat(found["activated_at"])
            if datetime.now() > activated + timedelta(days=1):
                return jsonify({"status": "expired", "reason": "Key expired"}), 403
        elif found["type"] == "week":
            activated = datetime.fromisoformat(found["activated_at"])
            if datetime.now() > activated + timedelta(weeks=1):
                return jsonify({"status": "expired", "reason": "Key expired"}), 403

        return jsonify({"status": "valid", "key": key}), 200

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500
