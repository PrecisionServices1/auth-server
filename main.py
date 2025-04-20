@app.route("/check", methods=["POST"])
def check_key():
    try:
        data = request.get_json()
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
                return jsonify({"status": "expired", "reason": "Key expired"}), 403
            elif found["type"] == "week" and datetime.now() > activated_at + timedelta(weeks=1):
                return jsonify({"status": "expired", "reason": "Key expired"}), 403

        return jsonify({"status": "valid"}), 200

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500
