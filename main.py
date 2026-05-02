import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

NSW_PRIORITY = {
    "sydney": 3,
    "parramatta": 3,
    "auburn": 3,
    "bankstown": 3,
    "newcastle": 2,
    "wollongong": 2,
    "central coast": 2,
    "penrith": 2,
    "liverpool": 2,
    "blacktown": 2,
    "tamworth": 1,
    "armidale": 1,
    "coffs harbour": 1,
    "wagga": 1,
    "grafton": 1,
    "canberra": 1
}

KEYWORDS = ["hilux", "prado", "landcruiser", "hiace", "dmax", "corolla"]

ENGINES = ["1kd", "2kd", "2tr", "3rz", "1gr", "3l", "5l"]

PRICE_MIN = 200
PRICE_MAX = 18000

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_location_score(location):
    if not location:
        return 0
    loc = location.lower()
    for k, v in NSW_PRIORITY.items():
        if k in loc:
            return v
    return -2

def score(item):
    text = item["title"].lower()
    price = item["price"]
    location = item.get("location", "")

    s = 0

    if any(k in text for k in KEYWORDS):
        s += 3

    if any(e in text for e in ENGINES):
        s += 3

    if PRICE_MIN <= price <= PRICE_MAX:
        s += 3
    else:
        s -= 2

    s += get_location_score(location)

    return s

def ingest_data():
    # V4 placeholder ingestion layer (real sources added later)
    return [
        {"title": "Hilux 2TR manual Sydney ute", "price": 3500, "location": "Sydney NSW"},
        {"title": "Prado 1GR Newcastle clean", "price": 4200, "location": "Newcastle NSW"},
        {"title": "Hilux hulx rough car", "price": 1500, "location": "Tamworth NSW"},
        {"title": "BMW broken engine", "price": 900, "location": "Melbourne VIC"}
    ]

def main():
    items = ingest_data()

    for i in items:
        s = score(i)

        if s >= 7:
            tag = "🔥 HOT NSW DEAL"
        elif s >= 5:
            tag = "👍 GOOD DEAL"
        else:
            continue

        msg = f"""
{tag}

🚗 {i['title']}
📍 {i['location']}
💰 ${i['price']}
📊 Score: {s}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """

        send(msg)

if __name__ == "__main__":
    main()
