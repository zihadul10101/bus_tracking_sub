from flask import Blueprint, request, jsonify
from db import db
from bson import ObjectId
from utils.decorators import token_required
import datetime

student_bp = Blueprint('student', __name__)

# Student admin views
@student_bp.route('/students', methods=['GET'])
@token_required(roles=['admin'])
def list_students(current_user):
    students = list(db.users.find({"role": "student"}))
    for s in students:
        s["_id"] = str(s["_id"])
    return jsonify(students), 200

@student_bp.route('/students/<student_id>', methods=['GET'])
@token_required(roles=['admin'])
def get_student(current_user, student_id):
    try:
        student = db.users.find_one({"_id": ObjectId(student_id), "role": "student"})
    except:
        return jsonify({"message": "Invalid student ID format"}), 400
    if not student:
        return jsonify({"message": "Student not found"}), 404
    student["_id"] = str(student["_id"])
    return jsonify(student), 200

@student_bp.route('/students/<student_id>/activate', methods=['PUT'])
@token_required(roles=['admin'])
def activate_student(current_user, student_id):
    try:
        student = db.users.find_one({"_id": ObjectId(student_id), "role": "student"})
    except:
        return jsonify({"message": "Invalid student ID format"}), 400
    if not student:
        return jsonify({"message": "Student not found"}), 404
    db.users.update_one({"_id": ObjectId(student_id)}, {"$set": {"is_verified": True}})
    return jsonify({"message": f"Student {student_id} activated successfully"}), 200

@student_bp.route('/students/<student_id>/deactivate', methods=['PUT'])
@token_required(roles=['admin'])
def deactivate_student(current_user, student_id):
    try:
        student = db.users.find_one({"_id": ObjectId(student_id), "role": "student"})
    except:
        return jsonify({"message": "Invalid student ID format"}), 400
    if not student:
        return jsonify({"message": "Student not found"}), 404
    db.users.update_one({"_id": ObjectId(student_id)}, {"$set": {"is_verified": False}})
    return jsonify({"message": f"Student {student_id} deactivated successfully"}), 200

@student_bp.route('/students/<student_id>/subscription', methods=['GET'])
@token_required(roles=['admin'])
def get_student_subscription(current_user, student_id):
    try:
        student = db.users.find_one({"_id": ObjectId(student_id), "role": "student"})
    except:
        return jsonify({"message": "Invalid student ID format"}), 400
    if not student:
        return jsonify({"message": "Student not found"}), 404
    subscription_info = student.get("student_info", {}).get("subscription_status", "inactive")
    return jsonify({"subscription_status": subscription_info}), 200

# Student resources: blood requests & posts
@student_bp.route('/blood_requests', methods=['POST'])
@token_required(roles=['student'])
def create_blood_request(current_user):
    data = request.get_json() or {}
    if not all([data.get("bloodType"), data.get("quantity"), data.get("hospital"), data.get("contactName"), data.get("contactPhone")]):
        return jsonify({"message": "Missing required fields"}), 400
    blood_request = {
        "userId": ObjectId(current_user["_id"]),
        "bloodType": data["bloodType"],
        "quantity": data["quantity"],
        "hospital": data["hospital"],
        "contactName": data["contactName"],
        "contactPhone": data["contactPhone"],
        "description": data.get("description", ""),
        "createdAt": datetime.datetime.utcnow(),
        "status": "pending"
    }
    res = db.blood_requests.insert_one(blood_request)
    return jsonify({"message": "Blood request created successfully", "blood_request_id": str(res.inserted_id)}), 201

@student_bp.route('/blood_requests/me', methods=['GET'])
@token_required(roles=['student'])
def get_my_blood_requests(current_user):
    docs = list(db.blood_requests.find({"userId": ObjectId(current_user["_id"])}))
    for d in docs:
        d["_id"] = str(d["_id"])
        d["userId"] = str(d["userId"])
    return jsonify(docs), 200

@student_bp.route('/blood_requests', methods=['GET'])
@token_required(roles=['student'])
def get_all_blood_requests(current_user):
    docs = list(db.blood_requests.find())
    for d in docs:
        d["_id"] = str(d["_id"])
        d["userId"] = str(d["userId"])
    return jsonify(docs), 200

# Housing posts
@student_bp.route('/housing_posts', methods=['POST'])
@token_required(roles=['student'])
def create_housing_post(current_user):
    data = request.get_json() or {}
    required = ["title", "description", "address", "rent", "bedrooms", "bathrooms", "contactName", "contactPhone"]
    if not all([data.get(k) for k in required]):
        return jsonify({"message": "Missing required fields"}), 400
    housing_post = {
        "userId": ObjectId(current_user["_id"]),
        "title": data["title"],
        "description": data["description"],
        "address": data["address"],
        "rent": data["rent"],
        "bedrooms": data["bedrooms"],
        "bathrooms": data["bathrooms"],
        "amenities": data.get("amenities", []),
        "contactName": data["contactName"],
        "contactPhone": data["contactPhone"],
        "createdAt": datetime.datetime.utcnow()
    }
    res = db.housing_posts.insert_one(housing_post)
    return jsonify({"message": "Housing post created successfully", "housing_post_id": str(res.inserted_id)}), 201

@student_bp.route('/housing_posts/me', methods=['GET'])
@token_required(roles=['student'])
def get_my_housing_posts(current_user):
    posts = list(db.housing_posts.find({"userId": ObjectId(current_user["_id"])}))
    for p in posts:
        p["_id"] = str(p["_id"])
        p["userId"] = str(p["userId"])
    return jsonify(posts), 200

# Tutoring posts
@student_bp.route('/tutoring_posts', methods=['POST'])
@token_required(roles=['student'])
def create_tutoring_post(current_user):
    data = request.get_json() or {}
    required = ["title", "subject", "description", "hourlyRate", "availability", "contactName", "contactPhone"]
    if not all([data.get(k) for k in required]):
        return jsonify({"message": "Missing required fields"}), 400
    tutoring_post = {
        "userId": ObjectId(current_user["_id"]),
        "title": data["title"],
        "subject": data["subject"],
        "description": data["description"],
        "hourlyRate": data["hourlyRate"],
        "availability": data["availability"],
        "contactName": data["contactName"],
        "contactPhone": data["contactPhone"],
        "createdAt": datetime.datetime.utcnow()
    }
    res = db.tutoring_posts.insert_one(tutoring_post)
    return jsonify({"message": "Tutoring post created successfully", "tutoring_post_id": str(res.inserted_id)}), 201

@student_bp.route('/tutoring_posts/me', methods=['GET'])
@token_required(roles=['student'])
def get_my_tutoring_posts(current_user):
    posts = list(db.tutoring_posts.find({"userId": ObjectId(current_user["_id"])}))
    for p in posts:
        p["_id"] = str(p["_id"])
        p["userId"] = str(p["userId"])
    return jsonify(posts), 200

@student_bp.route('/tutoring_posts', methods=['GET'])
@token_required(roles=['student'])
def get_all_tutoring_posts(current_user):
    posts = list(db.tutoring_posts.find())
    for p in posts:
        p["_id"] = str(p["_id"])
        p["userId"] = str(p["userId"])
    return jsonify(posts), 200

# Emergency contacts
@student_bp.route('/student/emergency_contacts', methods=['PUT'])
@token_required(roles=['student'])
def update_emergency_contacts(current_user):
    data = request.get_json() or {}
    emergency_contacts = data.get("emergency_contacts")
    if not isinstance(emergency_contacts, list):
        return jsonify({"message": "Emergency contacts must be a list"}), 400
    for contact in emergency_contacts:
        if not all([contact.get("name"), contact.get("relationship"), contact.get("phone")]):
            return jsonify({"message": "Missing required fields in emergency contact"}), 400
    try:
        db.users.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": {"student_info.emergency_contacts": emergency_contacts}})
        return jsonify({"message": "Emergency contacts updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error accessing database", "error": str(e)}), 500

@student_bp.route('/student/emergency_contacts', methods=['GET'])
@token_required(roles=['student'])
def get_emergency_contacts(current_user):
    try:
        student = db.users.find_one({"_id": ObjectId(current_user["_id"])})
        if not student:
            return jsonify({"message": "Student not found"}), 404
        emergency_contacts = student.get("student_info", {}).get("emergency_contacts", [])
        return jsonify(emergency_contacts), 200
    except Exception as e:
        return jsonify({"message": "Error accessing database", "error": str(e)}), 500
