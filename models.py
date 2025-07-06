from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Coach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    game = db.Column(db.String(50))
    level = db.Column(db.String(50))  # Basit, Orta, Pro, Oyun Ustası
    zoom_email = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    coach_id = db.Column(db.Integer, db.ForeignKey("coach.id"))
    price = db.Column(db.Float)
    session_id = db.Column(db.String(100))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey("coach.id"))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
