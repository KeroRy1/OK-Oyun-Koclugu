def calculate_price(level, is_first):
    base_prices = {
        "Basit": 50,
        "Orta": 100,
        "Pro": 150,
        "Oyun Ustası": 200
    }
    price = base_prices.get(level, 100)
    return price * 0.8 if is_first else price

def is_first_purchase(user_id):
    from models import Order
    return Order.query.filter_by(user_id=user_id).count() == 0

def create_zoom_meeting(email):
    return "https://zoom.us/fake-meeting-link"
