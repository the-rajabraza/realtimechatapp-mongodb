from flask_socketio import join_room, emit
from flask import session
import dbfunctions

def register_socketio_handlers(socketio, db):
    @socketio.on('connect')
    def handle_connect():
        username = session.get('username')
        if username:
            join_room(username)

    @socketio.on('send_message')
    def handle_message(data):
        message = data['message']
        username = data['username']
        partner = data['partner']

        # Save the message to the database
        message_id = dbfunctions.save_message(db, username, partner, message)

        # Emit the message to both users
        emit('receive_message', {'id': message_id, 'message': message, 'username': username}, room=partner)
        emit('receive_message', {'id': message_id, 'message': message, 'username': username}, room=username)

    @socketio.on('typing')
    def handle_typing(data):
        username = data['username']
        partner = data['partner']
        is_typing = data['is_typing']

        emit('user_typing', {'username': username, 'is_typing': is_typing}, room=partner)

    @socketio.on('mark_read')
    def handle_mark_read(data):
        message_id = data['message_id']
        reader = data['reader']
        sender = data['sender']

        dbfunctions.mark_message_as_read(db, message_id, reader)
        emit('message_read', {'message_id': message_id, 'reader': reader}, room=sender)

    @socketio.on('get_user_profile')
    def handle_get_user_profile(data):
        username = data['username']
        profile = dbfunctions.get_user_profile(db, username)
        emit('user_profile', {'username': username, 'avatar': profile.get('avatar'), 'status_message': profile.get('status_message')})

    @socketio.on('update_user_profile')
    def handle_update_user_profile(data):
        username = data['username']
        avatar = data['avatar']
        status_message = data['status_message']

        dbfunctions.update_user_profile(db, username, avatar, status_message)
        emit('profile_updated', {'username': username, 'avatar': avatar, 'status_message': status_message}, broadcast=True)