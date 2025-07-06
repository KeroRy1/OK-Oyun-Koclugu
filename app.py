import os
import logging
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import stripe
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Coach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.String(500), nullable=False)
    contact = db.Column(db.Column(db.String(200), nullable=False))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(200), unique=True, nullable=False)
    game = db.Column(db.String(50), nullable=False)
    package = db.Column(db.String(50), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.id'))
    coach = db.relationship('Coach')

TIME_SLOTS = [
    "16:00-17:00", "17:00-18:00", "18:00-19:00",
    "19:00-20:00", "20:00-21:00", "21:00-22:00"
]

games = ["Valorant", "CS2", "LoL"]
packages = [
    {"name": "Basit",  "price_tl": 400,  "features": ["Canlı Ders"]},
    {"name": "Orta",   "price_tl": 600,  "features": ["Canlı Ders", "PDF Rehber"]},
    {"name": "Pro",    "price_tl": 1000, "features": ["Canlı Ders", "PDF Rehber", "Özel Koçluk"]}
]

def seed_coaches():
    if not Coach.query.first():
        sample_coaches = [
            Coach(name="Ali",    game="Valorant", level="Basit",  availability="18:00-19:00,20:00-21:00", contact="discord.gg/ali"),
            Coach(name="Ayşe",   game="CS2",      level="Basit",  availability="19:00-20:00,21:00-22:00", contact="discord.gg/ayse"),
            Coach(name="Mehmet", game="LoL",      level="Basit",  availability="18:00-19:00,21:00-22:00", contact="discord.gg/mehmet"),
            Coach(name="Burcu",  game="Valorant", level="Orta",   availability="17:00-18:00,19:00-20:00", contact="discord.gg/burcu"),
            Coach(name="Cem",    game="CS2",      level="Orta",   availability="18:00-19:00,20:00-21:00", contact="discord.gg/cem"),
            Coach(name="Deniz",  game="LoL",      level="Orta",   availability="17:00-18:00,21:00-22:00", contact="discord.gg/deniz"),
            Coach(name="Elif",   game="Valorant", level="Pro",    availability="16:00-17:00,18:00-19:00", contact="discord.gg/elif"),
            Coach(name="Fatih",  game="CS2",      level="Pro",    availability="17:00-18:00,20:00-21:00", contact="discord.gg/fatih"),
            Coach(name="Gizem",  game="LoL",      level="Pro",    availability="16:00-17:00,21:00-22:00", contact="discord.gg/gizem")
        ]
        db.session.bulk_save_objects(sample_coaches)
        db.session.commit()

@app.route("/")
def index():
    return render_template("index.html", games=games, packages=packages, time_slots=TIME_SLOTS)

@app.route("/checkout", methods=["POST"])
def checkout():
    game = request.form.get("game")
    pkg = request.form.get("package")
    time_slot = request.form.get("time_slot")

    package = next((p for p in packages if p["name"] == pkg), None)
    if not game or not package or time_slot not in TIME_SLOTS:
        return "Geçersiz seçim.", 400

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "try",
                "product_data": {"name": f"{game} – {pkg} Koçluk Paketi"},
                "unit_amount": package["price_tl"] * 100
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=request.url_root + "success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.url_root + "cancel"
    )

    order = Order(session_id=session.id, game=game, package=pkg, time_slot=time_slot)
    db.session.add(order)
    db.session.commit()

    return redirect(session.url, code=303)

@app.route("/success")
def success():
    session_id = request.args.get("session_id")
    order = Order.query.filter_by(session_id=session_id).first_or_404()

    candidates = Coach.query.filter_by(game=order.game, level=order.package).all()
    available = [c for c in candidates if order.time_slot in c.availability.split(",")]

    return render_template("success.html", coach_list=available, time_slot=order.time_slot)

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_coaches()
    app.run(host="0.0.0.0", debug=True)
