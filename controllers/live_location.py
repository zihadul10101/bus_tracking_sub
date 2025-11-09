from flask import Blueprint, request, jsonify
from db import db
from bson import ObjectId
from utils.decorators import token_required
import datetime

live_bp = Blueprint('live', __name__)

@live_bp.route('/driver/location', methods=['POST'])
@token_required(roles=['driver'])
def post_location(current_user):
    data = request.get_json() or {}
    busId = data.get("busId")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    if not all([latitude, longitude, busId]):
        return jsonify({"message": "Missing required fields"}), 400
    try:
        bus = db.buses.find_one({"_id": ObjectId(busId)})
        if not bus:
            return jsonify({"message": "Bus not found"}), 404
    except:
        return jsonify({"message": "Invalid bus ID format"}), 400
    location = {
        "driverId": ObjectId(current_user["_id"]),
        "busId": ObjectId(busId),
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.datetime.utcnow()
    }
    db.live_locations.insert_one(location)
    return jsonify({"message": "Location updated successfully"}), 200

@live_bp.route('/locations', methods=['GET'])
@token_required(roles=['student', 'admin', 'driver'])
def get_locations(current_user):
    latest_locations = []
    buses = list(db.buses.find())
    for bus in buses:
        latest_location = db.live_locations.find_one({"busId": ObjectId(bus["_id"])}, sort=[("timestamp", -1)])
        if latest_location:
            latest_location["_id"] = str(latest_location["_id"])
            latest_location["driverId"] = str(latest_location["driverId"])
            latest_location["busId"] = str(latest_location["busId"])
            latest_locations.append(latest_location)
    return jsonify(latest_locations), 200
