from datetime import date

from flask import request, jsonify, g

from config.db import pool
from socket_io import emit_to_room


def today_date():
    return date.today().isoformat()


def check_in():
    user_id = g.user['id']
    d = today_date()

    existing = pool.query('SELECT * FROM attendance WHERE user_id = %s AND date = %s', [user_id, d])
    if existing and existing[0].get('check_in_time'):
        return jsonify({'success': False, 'message': 'Already checked in today'}), 409

    if existing:
        pool.execute(
            'UPDATE attendance SET check_in_time = NOW(), status = "Present" WHERE id = %s',
            [existing[0]['id']],
        )
        rows = pool.query('SELECT * FROM attendance WHERE id = %s', [existing[0]['id']])
    else:
        result = pool.execute(
            'INSERT INTO attendance (user_id, date, check_in_time, status) VALUES (%s, %s, NOW(), "Present")',
            [user_id, d],
        )
        rows = pool.query('SELECT * FROM attendance WHERE id = %s', [result['insert_id']])
    record = rows[0]

    emit_to_room('role:HR', 'attendance:updated', {'userId': user_id, 'record': record})
    return jsonify({'success': True, 'record': record}), 201


def check_out():
    user_id = g.user['id']
    d = today_date()

    rows = pool.query('SELECT * FROM attendance WHERE user_id = %s AND date = %s', [user_id, d])
    if not rows or not rows[0].get('check_in_time'):
        return jsonify({'success': False, 'message': 'You must check in before checking out'}), 400
    if rows[0].get('check_out_time'):
        return jsonify({'success': False, 'message': 'Already checked out today'}), 409

    pool.execute('UPDATE attendance SET check_out_time = NOW() WHERE id = %s', [rows[0]['id']])
    updated_rows = pool.query('SELECT * FROM attendance WHERE id = %s', [rows[0]['id']])
    record = updated_rows[0]

    emit_to_room('role:HR', 'attendance:updated', {'userId': user_id, 'record': record})
    return jsonify({'success': True, 'record': record})



def get_my_attendance():
    from_ = request.args.get('from')
    to = request.args.get('to')
    params = [g.user['id']]
    sql = 'SELECT * FROM attendance WHERE user_id = %s'
    if from_:
        sql += ' AND date >= %s'
        params.append(from_)
    if to:
        sql += ' AND date <= %s'
        params.append(to)
    sql += ' ORDER BY date DESC'
    rows = pool.query(sql, params)
    return jsonify({'success': True, 'records': rows})



def get_all_attendance():
    from_ = request.args.get('from')
    to = request.args.get('to')
    user_id = request.args.get('userId')
    params = []
    sql = """SELECT a.*, u.employee_id, u.full_name FROM attendance a
             JOIN users u ON u.id = a.user_id WHERE 1=1"""
    if from_:
        sql += ' AND a.date >= %s'
        params.append(from_)
    if to:
        sql += ' AND a.date <= %s'
        params.append(to)
    if user_id:
        sql += ' AND a.user_id = %s'
        params.append(user_id)
    sql += ' ORDER BY a.date DESC'
    rows = pool.query(sql, params)
    return jsonify({'success': True, 'records': rows})



def adjust_attendance(id):
    body = request.get_json(silent=True) or {}
    updates = {}
    if body.get('status'):
        updates['status'] = body['status']
    if 'check_in_time' in body:
        updates['check_in_time'] = body['check_in_time']
    if 'check_out_time' in body:
        updates['check_out_time'] = body['check_out_time']

    if not updates:
        return jsonify({'success': False, 'message': 'No fields to update'}), 400

    set_clause = ', '.join(f'{k} = %s' for k in updates)
    result = pool.execute(f'UPDATE attendance SET {set_clause} WHERE id = %s', [*updates.values(), id])
    if not result['affected_rows']:
        return jsonify({'success': False, 'message': 'Record not found'}), 404

    rows = pool.query('SELECT * FROM attendance WHERE id = %s', [id])
    record = rows[0]
    emit_to_room(f"user:{record['user_id']}", 'attendance:updated', {'userId': record['user_id'], 'record': record})
    return jsonify({'success': True, 'record': record})
