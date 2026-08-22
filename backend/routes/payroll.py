
from flask import Blueprint

from middleware.auth import authenticate
from middleware.role import require_role
from controllers.payroll_controller import get_my_payroll, get_all_payroll, upsert_payroll

payroll_bp = Blueprint('payroll', __name__)

payroll_bp.get('/me')(authenticate(get_my_payroll))
payroll_bp.get('/')(authenticate(require_role('HR')(get_all_payroll)))
payroll_bp.put('/<user_id>')(authenticate(require_role('HR')(upsert_payroll)))
