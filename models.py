from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Coach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    game = db.Column(db.String(50))
    level = db.Column(db.String(50))
    zoom_email = db.Column(db.String(100))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    coach_id = db.Column(db.Integer)
    price = db.Column(db.Float)
    session_id = db.Column(db.String(100))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
