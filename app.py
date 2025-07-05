import os
import logging
from flask import Flask, render_template, request, redirect
import stripe
from dotenv import load_dotenv

# Yerelde .env dosyasını yükle (Render’da .env kullanılmaz)
load_dotenv()

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Stripe gizli anahtarını ortam değişkeninden al
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Oyun ve paket bilgileri (TL cinsinden)
games = ["Valorant", "CS2", "LoL"]
packages = [
    {"name": "Basit", "price_tl": 400, "features": ["Canlı Ders"]},
    {"name": "Orta",  "price_tl": 600, "features": ["Canlı Ders", "PDF Rehber"]},
    {"name": "Pro",   "price_tl": 1000, "features": ["Canlı Ders", "PDF Rehber", "Özel Koçluk"]}
]

@app.route("/")
def index():
    return render_template("index.html", games=games, packages=packages)

@app.route("/checkout", methods=["POST"])
def checkout():
    game = request.form.get("game")
    pkg  = request.form.get("package")
    app.logger.debug(f"Checkout isteği: oyun={game}, paket={pkg}")

    package = next((p for p in packages if p["name"] == pkg), None)
    if not game or not package:
        app.logger.error("Geçersiz oyun veya paket seçimi")
        return "Oyun veya paket seçimi hatalı.", 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "try",
                    "product_data": {
                        "name": f"{game} – {package['name']} Koçluk Paketi"
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

    except Exception as e:
        app.logger.error(f"Stripe Checkout Hatası: {e}")
        return f"Ödeme sırasında hata oluştu: {e}", 500

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
