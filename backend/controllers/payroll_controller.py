
from flask import request, jsonify, g

from config.db import pool
from socket_io import emit_to_room


def compute_net(basic, allowances, deductions):
    return float(basic or 0) + float(allowances or 0) - float(deductions or 0)


# GET /api/payroll/me
def get_my_payroll():
    rows = pool.query('SELECT * FROM payroll WHERE user_id = %s', [g.user['id']])
    if not rows:
        return jsonify({'success': False, 'message': 'No payroll record found'}), 404
    return jsonify({'success': True, 'payroll': rows[0]})


# GET /api/payroll (admin)
def get_all_payroll():
    rows = pool.query(
        """SELECT p.*, u.employee_id, u.full_name FROM payroll p
           JOIN users u ON u.id = p.user_id ORDER BY u.full_name ASC"""
    )
    return jsonify({'success': True, 'records': rows})


# PUT /api/payroll/<user_id> (admin updates structure, recomputes net)
def upsert_payroll(user_id):
    body = request.get_json(silent=True) or {}
    basic_salary = body.get('basicSalary')
    allowances = body.get('allowances')
    deductions = body.get('deductions')
    if basic_salary is None:
        return jsonify({'success': False, 'message': 'basicSalary is required'}), 400
    net = compute_net(basic_salary, allowances, deductions)

    existing = pool.query('SELECT id FROM payroll WHERE user_id = %s', [user_id])
    if existing:
        pool.execute(
            'UPDATE payroll SET basic_salary = %s, allowances = %s, deductions = %s, net_salary = %s WHERE user_id = %s',
            [basic_salary, allowances or 0, deductions or 0, net, user_id],
        )
    else:
        pool.execute(
            """INSERT INTO payroll (user_id, basic_salary, allowances, deductions, net_salary)
               VALUES (%s, %s, %s, %s, %s)""",
            [user_id, basic_salary, allowances or 0, deductions or 0, net],
        )

    rows = pool.query('SELECT * FROM payroll WHERE user_id = %s', [user_id])
    record = rows[0]
    emit_to_room(f'user:{user_id}', 'payroll:updated', {'record': record})
    return jsonify({'success': True, 'payroll': record})
