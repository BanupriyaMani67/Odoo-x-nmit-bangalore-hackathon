"""
HRMS backend entry point.

Stack:
Flask + Flask-SocketIO + PyMySQL

Provides:
- REST API
- CORS
- Socket.IO
- Authentication routes
- User routes
- Attendance routes
- Leave routes
- Payroll routes
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from uvicorn.middleware.wsgi import WSGIMiddleware

load_dotenv(Path(__file__).resolve().parent / ".env")

from socket_io import socketio
from routes.auth import auth_bp
from routes.users import users_bp
from routes.attendance import attendance_bp
from routes.leaves import leaves_bp
from routes.payroll import payroll_bp


# Create Flask application
flask_app = Flask(__name__)

# Frontend URL
CLIENT_URL = os.environ.get(
    "CLIENT_URL",
    "http://localhost:5173"
)

# Enable CORS
CORS(flask_app, origins=[CLIENT_URL])


# Health check
@flask_app.get("/")
def root():
    return jsonify({
        "success": True,
        "message": "HRMS API is running"
    })


@flask_app.get("/api/health")
def health():
    return jsonify({
        "success": True,
        "message": "HRMS API is running"
    })


# Register API routes
flask_app.register_blueprint(
    auth_bp,
    url_prefix="/api/auth"
)

flask_app.register_blueprint(
    users_bp,
    url_prefix="/api/users"
)

flask_app.register_blueprint(
    attendance_bp,
    url_prefix="/api/attendance"
)

flask_app.register_blueprint(
    leaves_bp,
    url_prefix="/api/leaves"
)

flask_app.register_blueprint(
    payroll_bp,
    url_prefix="/api/payroll"
)


# 404 handler
@flask_app.errorhandler(404)
def not_found(_err):
    return jsonify({
        "success": False,
        "message": "Not found"
    }), 404


# Central error handler
@flask_app.errorhandler(Exception)
def handle_error(err):
    print("ERROR:", err)

    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500


# Initialize Socket.IO
socketio.init_app(flask_app)

app = WSGIMiddleware(flask_app)


# Start server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print(
        f"HRMS backend listening on "
        f"http://localhost:{port}"
    )

    socketio.run(
        flask_app,
        host="0.0.0.0",
        port=port,
        debug=True
    )