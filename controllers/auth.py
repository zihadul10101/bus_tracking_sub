from flask import Blueprint, request, jsonify
from db import db
from utils.helpers import hash_password, verify_password
from utils.email import send_otp_email, send_reset_email  # ← FIXED: BOTH IMPORTED
import datetime
import jwt
import random
import string
import secrets
from config import SECRET_KEY, JWT_ALGORITHM


auth_bp = Blueprint('auth', __name__)

# Generate 6-digit OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Store OTP temporarily with expiry (10 minutes)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email").lower() if data.get("email") else None
    mobile = data.get("mobile")
    password = data.get("password")
    role = data.get("role")   

    if not all([name, email, mobile, password, role]):
        return jsonify({"message": "Missing required fields"}), 400

    if db.users.find_one({"email": email}):
        return jsonify({"message": "Email already registered"}), 400

    if db.pending_users.find_one({"email": email}):
        return jsonify({"message": "Registration already in progress. Check your email for OTP."}), 400

    # Hash password
    hashed_password = hash_password(password)

    # Generate OTP
    otp = generate_otp()
    otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    user = {
        "name": name,
        "email": email,
        "mobile": mobile,
        "password": hashed_password,
        "role": role,
        "is_verified": False,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "otp": otp,
        "otp_expiry": otp_expiry
    }

    # Role-wise extra fields
    if role == "student":
        user["student_info"] = {
            "department": data.get("department"),
            "subscription_status": "inactive"
        }
    elif role == "driver":
        user["driver_info"] = {
            "nid": data.get("nid"),
            "is_approved": False
        }

    # Store in pending
    db.pending_users.insert_one(user)

    # Send OTP via Email
    try:
        send_otp_email(email, name, otp)
    except Exception as e:
        db.pending_users.delete_one({"email": email})
        return jsonify({"message": "Failed to send OTP email", "error": str(e)}), 500

    return jsonify({
        "message": "OTP sent to your email. Please verify to complete registration.",
        "email": email
    }), 200


@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    email = data.get("email").lower() if data.get("email") else None
    otp = data.get("otp")

    if not all([email, otp]):
        return jsonify({"message": "Email and OTP are required"}), 400

    # Find pending user
    user = db.pending_users.find_one({"email": email})
    if not user:
        return jsonify({"message": "No registration found or already verified"}), 404

    # Check OTP and expiry
    if user.get("otp") != otp:
        return jsonify({"message": "Invalid OTP"}), 400

    if datetime.datetime.utcnow() > user["otp_expiry"]:
        db.pending_users.delete_one({"email": email})
        return jsonify({"message": "OTP expired. Please register again."}), 400

    # OTP Valid → Move to users
    user["is_verified"] = True
    user["email_verified_at"] = datetime.datetime.utcnow()
    
    # Remove OTP fields
    user.pop("otp", None)
    user.pop("otp_expiry", None)

    db.users.insert_one(user)
    db.pending_users.delete_one({"email": email})

    return jsonify({"message": "Email verified! Registration successful."}), 200


@auth_bp.route('/resend_otp', methods=['POST'])
def resend_otp():
    data = request.get_json() or {}
    email = data.get("email").lower() if data.get("email") else None

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = db.pending_users.find_one({"email": email})
    if not user:
        return jsonify({"message": "No pending registration found"}), 404

    # Generate new OTP
    new_otp = generate_otp()
    new_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    db.pending_users.update_one(
        {"email": email},
        {"$set": {"otp": new_otp, "otp_expiry": new_expiry}}
    )

    try:
        send_otp_email(email, user["name"], new_otp)
    except Exception as e:
        return jsonify({"message": "Failed to resend OTP", "error": str(e)}), 500

    return jsonify({"message": "New OTP sent to your email"}), 200


# Login remains same
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get("email").lower() if data.get("email") else None
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    user = db.users.find_one({"email": email})
    if not user or not user.get("is_verified", False):
        return jsonify({"message": "Invalid credentials or unverified account"}), 401

    if verify_password(password, user["password"]):
        payload = {
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return jsonify({
            "message": "Login successful",
            "token": token,
            "role": user['role']
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401

    # Generate secure reset token
def generate_reset_token():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

# ──────────────────────────────────────────────────────────────
# 1. FORGOT PASSWORD → Send Reset Link
# ──────────────────────────────────────────────────────────────
@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").lower()

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = db.users.find_one({"email": email, "is_verified": True})
    if not user:
        return jsonify({"message": "If your email exists, a reset link has been sent."}), 200

    token = generate_reset_token()
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

    db.password_resets.update_one(
        {"email": email},
        {"$set": {"token": token, "expiry": expiry}},
        upsert=True
    )

    reset_link = f"http://localhost:3000/reset-password?token={token}&email={email}"

    if send_reset_email(email, user["name"], reset_link):
        return jsonify({"message": "Reset link sent to your email!"}), 200
    else:
        return jsonify({"message": "Failed to send email. Check terminal."}), 500


# ──────────────────────────────────────────────────────────────
# 2. RESET PASSWORD → Verify Token & Update Password
# ──────────────────────────────────────────────────────────────
@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    email = data.get("email", "").lower()
    token = data.get("token")
    new_password = data.get("new_password")

    if not all([email, token, new_password]):
        return jsonify({"message": "All fields are required"}), 400

    if len(new_password) < 6:
        return jsonify({"message": "Password must be 6+ characters"}), 400

    # Find reset token
    reset_doc = db.password_resets.find_one({"email": email, "token": token})
    if not reset_doc:
        return jsonify({"message": "Invalid or expired reset link"}), 400

    if datetime.datetime.utcnow() > reset_doc["expiry"]:
        db.password_resets.delete_one({"email": email})
        return jsonify({"message": "Reset link expired"}), 400

    # Update password
    hashed = hash_password(new_password)
    db.users.update_one(
        {"email": email},
        {"$set": {"password": hashed, "updated_at": datetime.datetime.utcnow()}}
    )

    # Delete token after use
    db.password_resets.delete_one({"email": email})

    return jsonify({"message": "Password reset successful! You can now login."}), 200