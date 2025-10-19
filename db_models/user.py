from repository.database import db
from datetime import datetime

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  sent_messages = db.relationship('Message',
                                  foreign_keys='Message.sender_id',
                                  backref='sender', lazy=True)
  
  received_messages = db.relationship('Message',
                                      foreign_keys='Message.receiver_id',
                                      backref='receiver', lazy=True)