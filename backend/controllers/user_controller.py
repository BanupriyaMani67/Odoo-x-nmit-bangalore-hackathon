
from flask import g, jsonify, request

from config.db import pool


def sanitize_user(user):
    return {key: value for key, value in user.items() if key != 'password_hash'}


def get_me():
    rows = pool.query('SELECT * FROM users WHERE id = %s', [g.user['id']])
    if not rows:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'user': sanitize_user(rows[0])})


def _update_user(user_id, body, allowed_fields):
    updates = {
        field: body[key]
        for key, field in allowed_fields.items()
        if key in body
    }
    if not updates:
        return None
    clause = ', '.join(f'{field} = %s' for field in updates)
    values = [*updates.values(), user_id]
    return pool.execute(f'UPDATE users SET {clause} WHERE id = %s', values)


def update_me():
    body = request.get_json(silent=True) or {}
    result = _update_user(g.user['id'], body, {
        'fullName': 'full_name',
        'address': 'address',
        'phone': 'phone',
        'profilePicture': 'profile_picture',
        'jobTitle': 'job_title',
        'department': 'department',
    })
    if result is None:
        return jsonify({'success': False, 'message': 'No fields to update'}), 400
    return get_me()


def list_users():
    rows = pool.query(
        'SELECT * FROM users ORDER BY full_name ASC'
    )
    return jsonify({'success': True, 'users': [sanitize_user(row) for row in rows]})


def update_user(id):
    body = request.get_json(silent=True) or {}
    result = _update_user(id, body, {
        'employeeId': 'employee_id',
        'email': 'email',
        'role': 'role',
        'fullName': 'full_name',
        'address': 'address',
        'phone': 'phone',
        'profilePicture': 'profile_picture',
        'jobTitle': 'job_title',
        'department': 'department',
        'isVerified': 'is_verified',
    })
    if result is None:
        return jsonify({'success': False, 'message': 'No fields to update'}), 400
    rows = pool.query('SELECT * FROM users WHERE id = %s', [id])
    if not rows:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'user': sanitize_user(rows[0])})
