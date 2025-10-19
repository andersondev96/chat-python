from repository.database import db

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(255), nullable=False)
  created_at = db.Column(db.DateTime, nullable=False)

  sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)