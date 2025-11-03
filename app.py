from flask import Flask, render_template, request, jsonify
from repository.database import db
from db_models.user import User
from db_models.message import Message
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBHOOK'

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
  return render_template('index.html')

# Websockets
active_users = {}

@socketio.on('connect')
def handle_connect():
  print(f"Cliente {request.sid} conectou")

@socketio.on('disconnect')
def handle_disconnect():
  sid = request.sid
  if sid in active_users:
    username = active_users[sid]['username']
    del active_users[sid]

    # notifica todos que o usuário saiu
    socketio.emit('user_left', {
      'username': username,
      'timestamp': datetime.now().strftime('%H:%M')
    }, namespace='/')

    # Atualiza lista de usuários
    socketio.emit('update_users', {
      'users': [user['username'] for user in active_users.values()]
    }, namespace='/')

  print(f'Client {sid} has disconnected to the server')

@socketio.on("set_username")
def handle_set_username(data):
  username = data.get('username', 'Anônimo')

  # salva o usuário
  active_users[request.sid] = {
    'username': username,
    'connected_at': datetime.now()
  }

  # notifica todos
  emit('user_joined', {
    'username': username,
    'timestamp': datetime.now().strftime('%H:%M')
  }, broadcast=True)

  # atualiza a lista
  emit('update_users', {
    'users': [user['username'] for user in active_users.values()]
  }, broadcast=True)


@socketio.on('message')
def handle_message(data):
  username = active_users[request.sid]['username']

  message_data = {
    'username': username,
    'message': data.get('message', ''),
    'timestamp': datetime.now().strftime('%H:%M'),
    'sid': request.sid,
  }

  emit('message', message_data, broadcast=True)

if __name__ == '__main__':
  socketio.run(app, debug=True)