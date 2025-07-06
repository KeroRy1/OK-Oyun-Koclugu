from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Coach, Order, Feedback
from forms import FeedbackForm
from utils import calculate_price, is_first_purchase, create_zoom_meeting
from config import Config
import stripe
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
stripe.api_key = app.config["STRIPE_SECRET_KEY"]

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    coaches = Coach.query.all()
    return render_template("index.html", coaches=coaches)

@app.route("/coach/<int:coach_id>")
def coach_profile(coach_id):
    coach = Coach.query.get_or_404(coach_id)
    form = FeedbackForm()
    return render_template("coach_profile.html", coach=coach, form=form)

@app.route("/checkout/<int:coach_id>", methods=["POST"])
def checkout(coach_id):
    coach = Coach.query.get_or_404(coach_id)
    user_id = session.get("user_id", 1)
    selected_time = request.form.get("time")
    selected_package = request.form.get("package")

    if not selected_time or int(selected_time[:2]) < 8:
        return "Geçersiz saat seçimi.", 400

    price = calculate_price(selected_package, is_first_purchase(user_id))

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "try",
                    "product_data": {
                        "name": f"{coach.game} – {selected_package} ({selected_time})",
                        "description": f"Koç: {coach.name}"
                    },
                    "unit_amount": int(price * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=url_for("waiting_room", coach_id=coach.id, _external=True),
            cancel_url=url_for("index", _external=True)
        )

        new_order = Order(user_id=user_id, coach_id=coach.id, price=price, session_id=checkout_session.id)
        db.session.add(new_order)
        db.session.commit()

        return redirect(checkout_session.url)

    except Exception as e:
        return f"Stripe Checkout hatası: {str(e)}"

@app.route("/waiting/<int:coach_id>")
def waiting_room(coach_id):
    coach = Coach.query.get_or_404(coach_id)
    try:
        zoom_link = create_zoom_meeting(coach.zoom_email)
        return redirect(zoom_link)
    except Exception as e:
        return f"Zoom toplantısı oluşturulamadı: {str(e)}"

@app.route("/submit-feedback/<int:coach_id>", methods=["POST"])
def submit_feedback(coach_id):
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(coach_id=coach_id, rating=form.rating.data, comment=form.comment.data)
        db.session.add(feedback)
        db.session.commit()
    return redirect(url_for("coach_profile", coach_id=coach_id))

@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("index"))
    coaches = Coach.query.all()
    orders = Order.query.all()
    feedbacks = Feedback.query.all()
    return render_template("admin_dashboard.html", coaches=coaches, orders=orders, feedbacks=feedbacks)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
