
from flask import Blueprint

from middleware.auth import authenticate
from middleware.role import require_role
from controllers.attendance_controller import (
    check_in, check_out, get_my_attendance, get_all_attendance, adjust_attendance,
)

attendance_bp = Blueprint('attendance', __name__)

attendance_bp.post('/check-in')(authenticate(check_in))
attendance_bp.post('/check-out')(authenticate(check_out))
attendance_bp.get('/me')(authenticate(get_my_attendance))
attendance_bp.get('/')(authenticate(require_role('HR')(get_all_attendance)))
attendance_bp.patch('/<id>')(authenticate(require_role('HR')(adjust_attendance)))
