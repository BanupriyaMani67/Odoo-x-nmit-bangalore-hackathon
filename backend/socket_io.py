
from flask_socketio import SocketIO, join_room

socketio = SocketIO(cors_allowed_origins='*', async_mode='threading')


@socketio.on('connect')
def handle_connect():
    pass


@socketio.on('register')
def handle_register(data):
    user_id = data.get('userId') if data else None
    role = data.get('role') if data else None
    if user_id:
        join_room(f'user:{user_id}')
    if role:
        join_room(f'role:{role}')


@socketio.on('disconnect')
def handle_disconnect():
    pass


def emit_to_room(room, event, data):
    """Equivalent of Node's `getIO().to(room).emit(event, data)`."""
    socketio.emit(event, data, room=room)
