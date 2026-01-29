from flask import Blueprint, request, jsonify
from db.mongo import collection
from datetime import datetime

webhook = Blueprint("webhook", __name__)

@webhook.route("/webhook", methods=["POST"])
def github_webhook():
    payload = request.get_json(silent=True)
    event_type = request.headers.get("X-GitHub-Event")

    # Basic validation
    if not payload or not event_type:
        return jsonify({"ignored": True}), 200

    data = None

    # HANDLE PUSH EVENT
    if event_type == "push":
        ref = payload.get("ref")
        commit_hash = payload.get("after")
        pusher = payload.get("pusher", {}).get("name")

        if not ref or not commit_hash or not pusher:
            return jsonify({"error": "Malformed push payload"}), 400

        branch = ref.split("/")[-1]

        data = {
            "request_id": commit_hash,
            "author": pusher,
            "action": "PUSH",
            "from_branch": branch,
            "to_branch": branch,
            "timestamp": datetime.utcnow()
        }

    # HANDLE PULL REQUEST + MERGE EVENTS
    elif event_type == "pull_request":
        action_type = payload.get("action")
        pr = payload.get("pull_request")

        if not pr:
            return jsonify({"ignored": True}), 200

        # PULL REQUEST OPENED
        if action_type == "opened":
            data = {
                "request_id": str(pr.get("number")),
                "author": pr.get("user", {}).get("login"),
                "action": "PULL_REQUEST",
                "from_branch": pr.get("head", {}).get("ref"),
                "to_branch": pr.get("base", {}).get("ref"),
                "timestamp": datetime.utcnow()
            }

        # MERGE (PR CLOSED + MERGED = TRUE)
        elif action_type == "closed" and pr.get("merged"):
            data = {
                "request_id": str(pr.get("number")),
                "author": pr.get("user", {}).get("login"),
                "action": "MERGE",
                "from_branch": pr.get("head", {}).get("ref"),
                "to_branch": pr.get("base", {}).get("ref"),
                "timestamp": datetime.utcnow()
            }

        else:
            return jsonify({"ignored": True}), 200

    # IGNORE ALL OTHER EVENTS
    else:
        return jsonify({"ignored": True}), 200

    # PREVENT DUPLICATES (GitHub retries deliveries)
    if collection.find_one({
        "request_id": data["request_id"],
        "action": data["action"]
    }):
        return jsonify({"duplicate": True}), 200

    # STORE IN MONGODB
    collection.insert_one(data)

    return jsonify({"status": "stored"}), 200
