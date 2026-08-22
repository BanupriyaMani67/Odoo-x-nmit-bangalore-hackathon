
from flask import Blueprint

from middleware.auth import authenticate
from middleware.role import require_role
from controllers.leave_controller import apply_leave, get_my_leaves, get_all_leaves, decide_leave

leaves_bp = Blueprint('leaves', __name__)

leaves_bp.post('/')(authenticate(apply_leave))
leaves_bp.get('/me')(authenticate(get_my_leaves))
leaves_bp.get('/')(authenticate(require_role('HR')(get_all_leaves)))
leaves_bp.patch('/<id>')(authenticate(require_role('HR')(decide_leave)))
