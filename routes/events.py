from flask import Blueprint, jsonify
from db.mongo import collection

events = Blueprint("events", __name__)

@events.route("/events", methods=["GET"])
def get_events():
    data = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(20))
    return jsonify(data)
