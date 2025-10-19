from flask import Flask, render_template
from repository.database import db
from db_models.user import User
from db_models.message import Message
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBHOOK'

db.init_app(app)
socketio = SocketIO(app)

@app.route('/message', methods=['POST'])
def send_message():
  pass

@app.route('/messages', methods=['GET'])
def get_messages_page():
  return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)