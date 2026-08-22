
from flask import Blueprint

from middleware.auth import authenticate
from middleware.role import require_role
from controllers.user_controller import get_me, update_me, list_users, update_user

users_bp = Blueprint('users', __name__)

users_bp.get('/me')(authenticate(get_me))
users_bp.patch('/me')(authenticate(update_me))
users_bp.get('/')(authenticate(require_role('HR')(list_users)))
users_bp.patch('/<id>')(authenticate(require_role('HR')(update_user)))
