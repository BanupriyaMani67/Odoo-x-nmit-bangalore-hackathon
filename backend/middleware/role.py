
from functools import wraps

from flask import g, jsonify


def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'user', None)
            if not user:
                return jsonify({'success': False, 'message': 'Not authenticated'}), 401
            if user.get('role') not in roles:
                return jsonify({'success': False, 'message': 'Forbidden: insufficient role'}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
