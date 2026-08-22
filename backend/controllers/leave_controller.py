from datetime import datetime

from flask import request, jsonify, g

from config.db import pool
from socket_io import emit_to_room



def apply_leave():
    body = request.get_json(silent=True) or {}
    type_ = body.get('type')
    start_date = body.get('startDate')
    end_date = body.get('endDate')
    remarks = body.get('remarks')

    if not type_ or not start_date or not end_date:
        return jsonify({'success': False, 'message': 'type, startDate, endDate are required'}), 400
    if type_ not in ('Paid', 'Sick', 'Unpaid'):
        return jsonify({'success': False, 'message': 'type must be Paid, Sick, or Unpaid'}), 400
    if datetime.fromisoformat(start_date) > datetime.fromisoformat(end_date):
        return jsonify({'success': False, 'message': 'startDate must be before endDate'}), 400

    result = pool.execute(
        """INSERT INTO leave_requests (user_id, type, start_date, end_date, remarks, status)
           VALUES (%s, %s, %s, %s, %s, 'Pending')""",
        [g.user['id'], type_, start_date, end_date, remarks or None],
    )
    rows = pool.query(
        """SELECT l.*, u.employee_id, u.full_name FROM leave_requests l
           JOIN users u ON u.id = l.user_id WHERE l.id = %s""",
        [result['insert_id']],
    )
    record = rows[0]

    emit_to_room('role:HR', 'leave:created', {'record': record})
    return jsonify({'success': True, 'record': record}), 201


# GET /api/leaves/me
def get_my_leaves():
    rows = pool.query(
        'SELECT * FROM leave_requests WHERE user_id = %s ORDER BY created_at DESC',
        [g.user['id']],
    )
    return jsonify({'success': True, 'records': rows})


# GET /api/leaves (admin)
def get_all_leaves():
    status = request.args.get('status')
    params = []
    sql = """SELECT l.*, u.employee_id, u.full_name FROM leave_requests l
             JOIN users u ON u.id = l.user_id WHERE 1=1"""
    if status:
        sql += ' AND l.status = %s'
        params.append(status)
    sql += ' ORDER BY l.created_at DESC'
    rows = pool.query(sql, params)
    return jsonify({'success': True, 'records': rows})


# PATCH /api/leaves/<id> (admin approves/rejects with comment)
def decide_leave(id):
    body = request.get_json(silent=True) or {}
    status = body.get('status')
    admin_comment = body.get('adminComment')
    if status not in ('Approved', 'Rejected'):
        return jsonify({'success': False, 'message': 'status must be Approved or Rejected'}), 400

    result = pool.execute(
        'UPDATE leave_requests SET status = %s, admin_comment = %s WHERE id = %s',
        [status, admin_comment or None, id],
    )
    if not result['affected_rows']:
        return jsonify({'success': False, 'message': 'Leave request not found'}), 404

    rows = pool.query('SELECT * FROM leave_requests WHERE id = %s', [id])
    record = rows[0]

    emit_to_room(f"user:{record['user_id']}", 'leave:updated', {'record': record})
    emit_to_room('role:HR', 'leave:updated', {'record': record})
    return jsonify({'success': True, 'record': record})
