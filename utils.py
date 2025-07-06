def calculate_price(package, is_first):
    prices = {
        "Basit": 400,
        "Orta": 600,
        "Pro": 1000,
        "Oyun Ustası": 1500
    }
    price = prices.get(package, 600)
    return price * 0.8 if is_first else price

def is_first_purchase(user_id):
    from models import Order
    return Order.query.filter_by(user_id=user_id).count() == 0

def create_zoom_meeting(email):
    return "https://zoom.us/fake-meeting-link"
