import requests
from config import Config

def calculate_price(level, is_first):
    base_prices = {
        "Basit": 400,
        "Orta": 600,
        "Pro": 800,
        "Oyun Ustası": 1000
    }
    price = base_prices.get(level, 600)
    if is_first:
        return price * 0.70
    return price

def is_first_purchase(user_id):
    from models import Order
    return Order.query.filter_by(user_id=user_id).count() == 0

def create_zoom_meeting(user_email):
    headers = {
        "Authorization": f"Bearer {Config.ZOOM_JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": "Koçluk Dersi",
        "type": 1
    }
    response = requests.post(f"https://api.zoom.us/v2/users/{user_email}/meetings", json=payload, headers=headers)
    if response.status_code == 201:
        return response.json()["join_url"]
    return "/waiting-failed"
