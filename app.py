from flask import Flask, session, request, redirect, url_for
from flask_socketio import SocketIO
import os
from routes import register_routes
from socketio_handling import register_socketio_handlers
from dbconfig import get_database, ping_database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
socketio = SocketIO(app, async_mode='threading')

# MongoDB Configuration
db = get_database()
ping_database()

# Authentication check
@app.before_request
def check_auth():
    if request.endpoint and 'static' not in request.endpoint and request.endpoint != 'login':
        if 'username' not in session:
            return redirect(url_for('login'))

# Register routes and socketio handlers
register_routes(app, db, session)
register_socketio_handlers(socketio, db)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)