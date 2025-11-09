from functools import wraps
from flask import request, jsonify
import jwt
from config import SECRET_KEY, JWT_ALGORITHM
from db import db
from bson import ObjectId

def token_required(roles=None):
    if roles is None:
        roles = []

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            if auth_header and " " in auth_header:
                token = auth_header.split(" ")[1]

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
                current_user = db.users.find_one({'email': data.get('email')})
                if not current_user:
                    return jsonify({'message': 'Invalid Token!'}), 401

                if roles and current_user.get('role') not in roles:
                    return jsonify({'message': 'Unauthorized: Insufficient permissions'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Signature has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token!'}), 401
            except Exception as e:
                return jsonify({'message': f'Auth error: {str(e)}'}), 401

            # inject current_user into endpoint kwargs for simple usage
            return f(current_user, *args, **kwargs)
        return wrapper
    return decorator
