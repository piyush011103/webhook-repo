from flask import Blueprint, request, jsonify
from db.mongo import collection
from datetime import datetime

webhook = Blueprint("webhook", __name__)

@webhook.route("/webhook", methods=["POST"])
def github_webhook():
    payload = request.get_json(silent=True)

    # 1️⃣ Validate payload exists
    if not payload:
        return jsonify({"error": "Invalid payload"}), 400

    event_type = request.headers.get("X-GitHub-Event")

    # 2️⃣ Validate event type exists
    if not event_type:
        return jsonify({"ignored": True}), 200

    # 3️⃣ Handle PUSH event
    if event_type == "push":
        if "after" not in payload or "pusher" not in payload or "ref" not in payload:
            return jsonify({"error": "Malformed push payload"}), 400

        data = {
            "request_id": payload["after"],
            "author": payload["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,
            "to_branch": payload["ref"].split("/")[-1],
            "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        }

    # 4️⃣ Handle PULL REQUEST & MERGE
    elif event_type == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request")

        if not pr or action not in ["opened", "closed"]:
            return jsonify({"ignored": True}), 200

        is_merged = pr.get("merged", False)

        data = {
            "request_id": str(pr.get("id")),
            "author": pr.get("user", {}).get("login"),
            "action": "MERGE" if is_merged else "PULL_REQUEST",
            "from_branch": pr.get("head", {}).get("ref"),
            "to_branch": pr.get("base", {}).get("ref"),
            "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        }

    # 5️⃣ Ignore all other GitHub events
    else:
        return jsonify({"ignored": True}), 200

    # 6️⃣ Store in MongoDB
    collection.insert_one(data)

    return jsonify({"status": "stored"}), 200
