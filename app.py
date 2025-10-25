from flask import Flask, render_template, request, jsonify
from repository.database import db
from db_models.user import User
from db_models.message import Message
from flask_socketio import SocketIO, emit

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBHOOK'

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/message', methods=['POST'])
def send_message():
  data = request.get_json()

  if 'content' not in data or 'sender_id' not in data or 'receiver_id' not in data:
    return jsonify({ "message": "Invalid data"}), 400
  
  sender = User.query.get(data['sender_id'])
  receiver = User.query.get(data['receiver_id'])

  if not sender or not receiver:
    return jsonify({ "message": "Invalid sender or receiver"}), 400
  
  new_message = Message(content=data['content'], sender_id=data['sender_id'], receiver_id=data['receiver_id'])
  db.session.add(new_message)
  db.session.commit()

  # Envia a mensagem para todos os clientes conectados
  socketio.emit('message', {'message': new_message.content})

  return jsonify({ "message": new_message.content }), 201

@app.route('/user', methods=['POST'])
def create_user():
  data = request.get_json()

  if 'username' not in data:
    return jsonify({ "message": "Invalid data"}), 400
  
  existing_user = User.query.filter_by(username=data['username']).first()
  if existing_user:
    return jsonify({ "message": "User already exists"}), 400
  
  new_user = User(username=data['username'])
  db.session.add(new_user)
  db.session.commit()

  return jsonify({ "message": "User created successfully"}), 201


@app.route('/messages/<int:user_id>', methods=['GET'])
def get_messages_page(user_id):
  user = User.query.get(user_id)
  if not user:
    return jsonify({ "message": "User not found"}), 404
  
  messages = Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).all()

  message_list = []
  for message in messages:
    message_data = {
      "id": message.id,
      "content": message.content,
      "created_at": message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
      "sender_id": message.sender_id,
      "receiver_id": message.receiver_id
    }
    message_list.append(message_data)
  
  return jsonify(message_list)

@app.route('/')
def index():
  return render_template('index.html')

# Websockets
@socketio.on('connect')
def handle_connect():
  print("Client connected to the server")

@socketio.on('disconnect')
def handle_disconnect():
  print("Client has disconnected to the server")

@socketio.on('message')
def handle_message(data):
  print(f"Mensagem recebida: {data}")
  emit('new message', data, broadcast=True)

if __name__ == '__main__':
  socketio.run(app, debug=True)