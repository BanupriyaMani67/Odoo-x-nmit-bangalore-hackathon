import os
import re
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import request, jsonify

from config.db import pool
from services.mailer import send_verification_email
from services.google_auth import verify_google_token

PASSWORD_RE = re.compile(r'^(?=.*[A-Z])(?=.*\d).{8,}$')


def sign_token(user):
    expires_days = int(os.environ.get('JWT_EXPIRES_IN_DAYS', 7))
    payload = {
        'id': user['id'],
        'role': user['role'],
        'employeeId': user['employee_id'],
        'email': user['email'],
        'exp': datetime.now(timezone.utc) + timedelta(days=expires_days),
    }
    return jwt.encode(payload, os.environ.get('JWT_SECRET'), algorithm='HS256')


def sanitize_user(u):
    if not u:
        return u
    return {k: v for k, v in u.items() if k != 'password_hash'}


def register():
    try:
        body = request.get_json(silent=True) or {}
        employee_id = body.get('employeeId')
        email = body.get('email')
        password = body.get('password')
        role = body.get('role')
        full_name = body.get('fullName')

        if not employee_id or not email or not password or not role:
            return jsonify({'success': False, 'message': 'employeeId, email, password, role are required'}), 400
        if role not in ('Employee', 'HR'):
            return jsonify({'success': False, 'message': 'role must be Employee or HR'}), 400
        if not PASSWORD_RE.match(password):
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters and include an uppercase letter and a number',
            }), 400

        existing = pool.query(
            'SELECT id FROM users WHERE email = %s OR employee_id = %s',
            [email, employee_id],
        )
        if existing:
            return jsonify({'success': False, 'message': 'User with this email or employee ID already exists'}), 409

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10)).decode()
        verify_token = secrets.token_hex(32)

        result = pool.execute(
            """INSERT INTO users (employee_id, email, password_hash, role, full_name, is_verified, verify_token, auth_provider)
               VALUES (%s, %s, %s, %s, %s, 0, %s, 'local')""",
            [employee_id, email, password_hash, role, full_name or employee_id, verify_token],
        )

        try:
            send_verification_email(email, verify_token)
        except Exception as mail_err:  # noqa: BLE001
            print(f'Failed to send verification email: {mail_err}')

        return jsonify({
            'success': True,
            'message': 'Registered. Please check your email to verify your account.',
            'userId': result['insert_id'],
        }), 201
    except Exception as err:  # noqa: BLE001
        print(err)
        return jsonify({'success': False, 'message': 'Server error during registration'}), 500



def verify_email(token):
    try:
        rows = pool.query('SELECT id FROM users WHERE verify_token = %s', [token])
        if not rows:
            return jsonify({'success': False, 'message': 'Invalid or expired verification token'}), 400
        pool.execute(
            'UPDATE users SET is_verified = 1, verify_token = NULL WHERE id = %s',
            [rows[0]['id']],
        )
        return jsonify({'success': True, 'message': 'Email verified. You can now sign in.'})
    except Exception as err:  # noqa: BLE001
        print(err)
        return jsonify({'success': False, 'message': 'Server error during verification'}), 500



def login():
    try:
        body = request.get_json(silent=True) or {}
        email = body.get('email')
        password = body.get('password')
        if not email or not password:
            return jsonify({'success': False, 'message': 'email and password are required'}), 400

        rows = pool.query('SELECT * FROM users WHERE email = %s', [email])
        user = rows[0] if rows else None
        if not user or user.get('auth_provider') != 'local':
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        stored_hash = (user.get('password_hash') or '').encode()
        match = stored_hash and bcrypt.checkpw(password.encode(), stored_hash)
        if not match:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        if not user.get('is_verified'):
            return jsonify({'success': False, 'message': 'Please verify your email before signing in'}), 403

        token = sign_token(user)
        return jsonify({'success': True, 'token': token, 'user': sanitize_user(user)})
    except Exception as err:  
        print(err)
        return jsonify({'success': False, 'message': 'Server error during login'}), 500



def google_login():
    try:
        body = request.get_json(silent=True) or {}
        id_token = body.get('idToken')
        if not id_token:
            return jsonify({'success': False, 'message': 'idToken is required'}), 400

        payload = verify_google_token(id_token)
        if not payload or not payload.get('email'):
            return jsonify({'success': False, 'message': 'Invalid Google token'}), 401

        rows = pool.query('SELECT * FROM users WHERE email = %s', [payload['email']])
        user = rows[0] if rows else None

        if not user:
            # Auto-create on first Google login
            generated_employee_id = f'G-{int(datetime.now().timestamp() * 1000)}'
            result = pool.execute(
                """INSERT INTO users (employee_id, email, password_hash, role, full_name, is_verified, auth_provider)
                   VALUES (%s, %s, NULL, 'Employee', %s, 1, 'google')""",
                [generated_employee_id, payload['email'], payload.get('name') or payload['email']],
            )
            new_rows = pool.query('SELECT * FROM users WHERE id = %s', [result['insert_id']])
            user = new_rows[0]

        token = sign_token(user)
        return jsonify({'success': True, 'token': token, 'user': sanitize_user(user)})
    except Exception as err:  # noqa: BLE001
        print(err)
        return jsonify({'success': False, 'message': 'Google authentication failed'}), 401
