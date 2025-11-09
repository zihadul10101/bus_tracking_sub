from flask import Blueprint, request, jsonify
from db import db
from bson import ObjectId
from utils.decorators import token_required
import datetime

notices_bp = Blueprint('notices', __name__)

@notices_bp.route('/admin/notices', methods=['POST'])
@token_required(roles=['admin'])
def create_notice(current_user):
    data = request.get_json() or {}
    title = data.get("title")
    content = data.get("content")
    if not all([title, content]):
        return jsonify({"message": "Missing required fields"}), 400
    notice = {
        "adminId": ObjectId(current_user["_id"]),
        "title": title,
        "content": content,
        "createdAt": datetime.datetime.utcnow(),
        "updatedAt": datetime.datetime.utcnow()
    }
    res = db.academic_notices.insert_one(notice)
    return jsonify({"message": "Notice created successfully", "notice_id": str(res.inserted_id)}), 201

@notices_bp.route('/notices', methods=['GET'])
@token_required(roles=['student', 'admin', 'driver'])
def list_notices(current_user):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    start = (page - 1) * limit
    notices = list(db.academic_notices.find().sort([("createdAt", -1)]).skip(start).limit(limit))
    total_notices = db.academic_notices.count_documents({})
    for n in notices:
        n["_id"] = str(n["_id"])
        n["adminId"] = str(n["adminId"])
    return jsonify({
        "notices": notices,
        "page": page,
        "limit": limit,
        "total": total_notices,
        "pages": (total_notices + limit - 1) // limit
    }), 200

@notices_bp.route('/admin/notices/<notice_id>', methods=['GET'])
@token_required(roles=['admin'])
def get_notice(current_user, notice_id):
    try:
        notice = db.academic_notices.find_one({"_id": ObjectId(notice_id)})
    except:
        return jsonify({"message": "Invalid notice ID format"}), 400
    if not notice:
        return jsonify({"message": "Notice not found"}), 404
    notice["_id"] = str(notice["_id"])
    notice["adminId"] = str(notice["adminId"])
    return jsonify(notice), 200

@notices_bp.route('/admin/notices/<notice_id>', methods=['PUT'])
@token_required(roles=['admin'])
def update_notice(current_user, notice_id):
    try:
        notice = db.academic_notices.find_one({"_id": ObjectId(notice_id)})
    except:
        return jsonify({"message": "Invalid notice ID format"}), 400
    if not notice:
        return jsonify({"message": "Notice not found"}), 404
    data = request.get_json() or {}
    title = data.get("title")
    content = data.get("content")
    updated = {}
    if title:
        updated["title"] = title
    if content:
        updated["content"] = content
    updated["updatedAt"] = datetime.datetime.utcnow()
    db.academic_notices.update_one({"_id": ObjectId(notice_id)}, {"$set": updated})
    return jsonify({"message": "Notice updated successfully"}), 200

@notices_bp.route('/admin/notices/<notice_id>', methods=['DELETE'])
@token_required(roles=['admin'])
def delete_notice(current_user, notice_id):
    try:
        obj = ObjectId(notice_id)
    except:
        return jsonify({"message": "Invalid notice ID format"}), 400
    notice = db.academic_notices.find_one({"_id": obj})
    if not notice:
        return jsonify({"message": "Notice not found"}), 404
    db.academic_notices.delete_one({"_id": obj})
    return jsonify({"message": "Notice deleted successfully"}), 200
