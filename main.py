import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# -----------------------------
# NSW TARGET AREAS ONLY
# -----------------------------
NSW_LOCATIONS = [
    "sydney", "parramatta", "auburn", "bankstown",
    "newcastle", "central coast", "wollongong",
    "penrith", "liverpool", "blacktown",
    "tamworth", "armidale", "coffs harbour",
    "grafton", "wagga", "canberra", "goulburn"
]

# -----------------------------
# VEHICLE FILTERS
# -----------------------------
KEYWORDS = [
    "hilux", "prado", "landcruiser", "hiace",
    "corolla", "dmax", "isuzu", "ute"
]

ENGINES = [
    "1kd", "2kd", "2tr", "3rz", "1rz", "1gr",
    "3l", "5l", "2.8", "2.4", "3.0"
]

PRICE_MIN = 200
PRICE_MAX = 18000

# -----------------------------
# SEND MESSAGE
# -----------------------------
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

# -----------------------------
# NSW FILTER CHECK
# -----------------------------
def is_nsw(text):
    text = text.lower()
    return any(loc in text for loc in NSW_LOCATIONS)

# -----------------------------
# SCORING ENGINE
# -----------------------------
def score_item(title, price, location=""):
    t = title.lower()

    score = 0

    if any(k in t for k in KEYWORDS):
        score += 3

    if any(e in t for e in ENGINES):
        score += 3

    if PRICE_MIN <= price <= PRICE_MAX:
        score += 3
    else:
        score -= 2

    if is_nsw(title + " " + location):
        score += 3
    else:
        score -= 3

    return score

# -----------------------------
# DATA PLACEHOLDER (V4 → real scraper later)
# -----------------------------
def get_listings():
    return [
        {"title": "Hilux 2TR single cab Auburn NSW", "price": 3500, "location": "Sydney"},
        {"title": "Prado 1GR engine Newcastle", "price": 4200, "location": "Newcastle"},
        {"title": "Hilux hulx rough Tamworth", "price": 1800, "location": "Tamworth"},
        {"title": "Ford broken car Melbourne", "price": 900, "location": "Melbourne"}
    ]

# -----------------------------
# MAIN ENGINE
# -----------------------------
def main():
    listings = get_listings()

    for item in listings:
        title = item["title"]
        price = item["price"]
        location = item["location"]

        score = score_item(title, price, location)

        if score >= 7:
            status = "🔥 HOT NSW DEAL"
        elif score >= 5:
            status = "👍 GOOD DEAL"
        else:
            continue

        msg = f"""
{status}

🚗 {title}
📍 {location}
💰 ${price}
📊 Score: {score}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """

        send_message(msg)

if __name__ == "__main__":
    main()
