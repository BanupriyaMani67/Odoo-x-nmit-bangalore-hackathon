
import os
from functools import wraps

import jwt
from flask import request, g, jsonify


def authenticate(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        token = header[7:] if header.startswith('Bearer ') else None

        if not token:
            return jsonify({'success': False, 'message': 'No token provided'}), 401

        try:
            payload = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
            g.user = payload  # { id, role, employeeId, email }
        except jwt.PyJWTError:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        return fn(*args, **kwargs)

    return wrapper
