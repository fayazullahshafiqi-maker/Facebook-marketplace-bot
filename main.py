import os
import requests
import re
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# -----------------------------
# VEHICLE FILTER SYSTEM
# -----------------------------

KEYWORDS = [
    "hilux", "prado", "landcruiser", "land cruiser",
    "hiace", "corolla", "dmax", "isuzu", "ute"
]

MISSPELLINGS = [
    "hilux", "hiluxx", "hilx", "hulx", "hiluks",
    "prado", "pradoo", "pradooo",
    "landcruser", "landcruiser", "lc200", "lc300"
]

ENGINES = [
    "1kd", "2kd", "2tr", "3rz", "1rz", "1gr",
    "3l", "5l", "2.8", "2.4", "3.0"
]

PRICE_MIN = 200
PRICE_MAX = 18000

# -----------------------------
# MESSAGE SENDER
# -----------------------------

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

# -----------------------------
# SIMPLE AI SCORING
# -----------------------------

def score_item(title, price):
    title_low = title.lower()

    score = 0

    # keyword match
    if any(k in title_low for k in KEYWORDS):
        score += 3

    # engine match
    if any(e in title_low for e in ENGINES):
        score += 3

    # misspelling boost (we still catch them)
    if any(m in title_low for m in MISSPELLINGS):
        score += 2

    # price logic
    if PRICE_MIN <= price <= PRICE_MAX:
        score += 3
    else:
        score -= 2

    return score

# -----------------------------
# FAKE DATA SIMULATOR (V2 STEP)
# -----------------------------

def get_listings():
    # later we replace this with real Facebook Marketplace scraper
    return [
        {"title": "Toyota Hilux 2TR manual ute", "price": 3500},
        {"title": "Prado VX 1GR engine 2006", "price": 4200},
        {"title": "Hilux hulx workmate rough", "price": 1800},
        {"title": "BMW broken engine car", "price": 900}
    ]

# -----------------------------
# MAIN ENGINE
# -----------------------------

def main():
    listings = get_listings()

    for item in listings:
        title = item["title"]
        price = item["price"]

        score = score_item(title, price)

        if score >= 6:
            status = "🔥 HOT DEAL"
        elif score >= 4:
            status = "👍 GOOD DEAL"
        else:
            continue

        msg = f"""
{status}

🚗 {title}
💰 ${price}
📊 Score: {score}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """

        send_message(msg)

if __name__ == "__main__":
    main()
