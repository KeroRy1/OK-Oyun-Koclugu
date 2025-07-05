import os
from flask import Flask, render_template, request, redirect, url_for
import stripe

app = Flask(__name__)

# Stripe anahtarları (Render'da ortam değişkeni olarak ekleyin)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Desteklenen oyunlar ve paketler (TL cinsinden)
games = ["Valorant", "CS2", "LoL"]
packages = [
    {"name": "Basit", "price_tl": 400,  "features": ["Canlı Ders"]},
    {"name": "Orta",  "price_tl": 600,  "features": ["Canlı Ders", "PDF Rehber"]},
    {"name": "Pro",   "price_tl": 1000, "features": ["Canlı Ders", "PDF Rehber", "Özel Koçluk"]}
]

@app.route("/")
def index():
    # Publishable key da şablonda JS için lazım olabilir
    publishable_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    return render_template("index.html", games=games, packages=packages, publishable_key=publishable_key)

@app.route("/checkout", methods=["POST"])
def checkout():
    game   = request.form.get("game")
    pkg    = request.form.get("package")
    package = next((p for p in packages if p["name"] == pkg), None)
    if not game or not package:
        return "Oyun veya paket seçimi hatalı.", 400

    # Checkout Session oluştur
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "try",
                "product_data": {
                    "name": f"{game} - {package['name']} Koçluk Paketi"
                },
                "unit_amount": package["price_tl"] * 100
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=request.url_root + "success",
        cancel_url=request.url_root + "cancel"
    )
    return redirect(session.url, code=303)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
