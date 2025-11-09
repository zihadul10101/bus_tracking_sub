from flask import Blueprint, request, jsonify
from db import db
from bson import ObjectId
from utils.decorators import token_required
import datetime

admin_bp = Blueprint('admin', __name__)

# Bus endpoints
@admin_bp.route('/buses', methods=['POST'])
@token_required(roles=['admin'])
def create_bus(current_user):
    data = request.get_json() or {}
    bus_number = data.get("bus_number")
    route = data.get("route")
    capacity = data.get("capacity")
    if not all([bus_number, route, capacity]):
        return jsonify({"message": "Missing required fields"}), 400
    bus = {
        "bus_number": bus_number,
        "route": route,
        "capacity": capacity,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    res = db.buses.insert_one(bus)
    return jsonify({"message": "Bus created successfully", "bus_id": str(res.inserted_id)}), 201

@admin_bp.route('/buses/<bus_id>', methods=['GET'])
@token_required(roles=['admin'])
def get_bus(current_user, bus_id):
    try:
        bus = db.buses.find_one({"_id": ObjectId(bus_id)})
    except:
        return jsonify({"message": "Invalid bus ID format"}), 400
    if not bus:
        return jsonify({"message": "Bus not found"}), 404
    bus["_id"] = str(bus["_id"])
    return jsonify(bus), 200

@admin_bp.route('/buses/<bus_id>', methods=['PUT'])
@token_required(roles=['admin'])
def update_bus(current_user, bus_id):
    try:
        _ = db.buses.find_one({"_id": ObjectId(bus_id)})
    except:
        return jsonify({"message": "Invalid bus ID format"}), 400
    data = request.get_json() or {}
    bus_number = data.get("bus_number")
    route = data.get("route")
    capacity = data.get("capacity")
    if not all([bus_number, route, capacity]):
        return jsonify({"message": "Missing required fields"}), 400
    updated_bus = {
        "bus_number": bus_number,
        "route": route,
        "capacity": capacity,
        "updated_at": datetime.datetime.utcnow(),
    }
    db.buses.update_one({"_id": ObjectId(bus_id)}, {"$set": updated_bus})
    return jsonify({"message": "Bus updated successfully"}), 200

@admin_bp.route('/buses/<bus_id>', methods=['DELETE'])
@token_required(roles=['admin'])
def delete_bus(current_user, bus_id):
    try:
        _ = db.buses.find_one({"_id": ObjectId(bus_id)})
    except:
        return jsonify({"message": "Invalid bus ID format"}), 400
    db.buses.delete_one({"_id": ObjectId(bus_id)})
    return jsonify({"message": "Bus deleted successfully"}), 200

# Schedule endpoints
@admin_bp.route('/schedules', methods=['POST'])
@token_required(roles=['admin'])
def create_schedule(current_user):
    data = request.get_json() or {}
    bus_id = data.get("bus_id")
    route = data.get("route")
    departure_time = data.get("departure_time")
    arrival_time = data.get("arrival_time")
    days_of_week = data.get("days_of_week")
    if not all([bus_id, route, departure_time, arrival_time, days_of_week]):
        return jsonify({"message": "Missing required fields"}), 400
    try:
        bus = db.buses.find_one({"_id": ObjectId(bus_id)})
        if not bus:
            return jsonify({"message": "Bus not found"}), 400
    except:
        return jsonify({"message": "Invalid bus ID format"}), 400
    schedule = {
        "bus_id": ObjectId(bus_id),
        "route": route,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "days_of_week": days_of_week,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    res = db.schedules.insert_one(schedule)
    return jsonify({"message": "Schedule created successfully", "schedule_id": str(res.inserted_id)}), 201

@admin_bp.route('/schedules/<schedule_id>', methods=['GET'])
@token_required(roles=['admin'])
def get_schedule(current_user, schedule_id):
    try:
        schedule = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    except:
        return jsonify({"message": "Invalid schedule ID format"}), 400
    if not schedule:
        return jsonify({"message": "Schedule not found"}), 404
    schedule["_id"] = str(schedule["_id"])
    schedule["bus_id"] = str(schedule["bus_id"])
    return jsonify(schedule), 200

@admin_bp.route('/schedules/<schedule_id>', methods=['PUT'])
@token_required(roles=['admin'])
def update_schedule(current_user, schedule_id):
    try:
        schedule = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    except:
        return jsonify({"message": "Invalid schedule ID format"}), 400
    if not schedule:
        return jsonify({"message": "Schedule not found"}), 404
    data = request.get_json() or {}
    bus_id = data.get("bus_id")
    route = data.get("route")
    departure_time = data.get("departure_time")
    arrival_time = data.get("arrival_time")
    days_of_week = data.get("days_of_week")
    if not all([bus_id, route, departure_time, arrival_time, days_of_week]):
        return jsonify({"message": "Missing required fields"}), 400
    try:
        bus = db.buses.find_one({"_id": ObjectId(bus_id)})
        if not bus:
            return jsonify({"message": "Bus not found"}), 400
    except:
        return jsonify({"message": "Invalid bus ID format"}), 400
    updated_schedule = {
        "bus_id": ObjectId(bus_id),
        "route": route,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "days_of_week": days_of_week,
        "updated_at": datetime.datetime.utcnow(),
    }
    db.schedules.update_one({"_id": ObjectId(schedule_id)}, {"$set": updated_schedule})
    return jsonify({"message": "Schedule updated successfully"}), 200

@admin_bp.route('/schedules/<schedule_id>', methods=['DELETE'])
@token_required(roles=['admin'])
def delete_schedule(current_user, schedule_id):
    try:
        _ = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    except:
        return jsonify({"message": "Invalid schedule ID format"}), 400
    db.schedules.delete_one({"_id": ObjectId(schedule_id)})
    return jsonify({"message": "Schedule deleted successfully"}), 200

# Driver assignment
@admin_bp.route('/drivers/<driver_id>/assign', methods=['PUT'])
@token_required(roles=['admin'])
def assign_driver_to_bus(current_user, driver_id):
    data = request.get_json() or {}
    bus_id = data.get("bus_id")
    if not bus_id:
        return jsonify({"message": "Missing required field: bus_id"}), 400
    try:
        driver = db.users.find_one({"_id": ObjectId(driver_id), "role": "driver"})
        if not driver:
            return jsonify({"message": "Driver not found"}), 404
        bus = db.buses.find_one({"_id": ObjectId(bus_id)})
        if not bus:
            return jsonify({"message": "Bus not found"}), 404
    except:
        return jsonify({"message": "Invalid ID format"}), 400
    db.users.update_one({"_id": ObjectId(driver_id)}, {"$set": {"driver_info.assigned_bus": ObjectId(bus_id)}})
    return jsonify({"message": f"Driver {driver_id} assigned to bus {bus_id} successfully"}), 200

# Admin fetchers
@admin_bp.route('/admin/blood_requests', methods=['GET'])
@token_required(roles=['admin'])
def list_blood_requests(current_user):
    entries = list(db.blood_requests.find())
    for e in entries:
        e["_id"] = str(e["_id"])
        e["userId"] = str(e["userId"])
    return jsonify(entries), 200

@admin_bp.route('/admin/housing_posts', methods=['GET'])
@token_required(roles=['admin'])
def list_housing_posts(current_user):
    posts = list(db.housing_posts.find())
    for p in posts:
        p["_id"] = str(p["_id"])
        p["userId"] = str(p["userId"])
    return jsonify(posts), 200

@admin_bp.route('/admin/tutoring_posts', methods=['GET'])
@token_required(roles=['admin'])
def list_tutoring_posts(current_user):
    posts = list(db.tutoring_posts.find())
    for p in posts:
        p["_id"] = str(p["_id"])
        p["userId"] = str(p["userId"])
    return jsonify(posts), 200
