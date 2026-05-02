import os
import requests
import time
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# -----------------------------
# NSW + CANBERRA SYSTEM
# -----------------------------
NSW_LOCATIONS = [
    "sydney", "parramatta", "auburn", "bankstown",
    "newcastle", "wollongong", "penrith",
    "liverpool", "blacktown", "central coast",
    "canberra"
]

KEYWORDS = ["hilux", "prado", "landcruiser", "hiace", "dmax"]
ENGINES = ["1kd", "2kd", "2tr", "3rz", "1gr"]

PRICE_MIN = 200
PRICE_MAX = 18000

# -----------------------------
# TELEGRAM SENDER
# -----------------------------
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -----------------------------
# NSW CHECK
# -----------------------------
def is_nsw(text):
    t = text.lower()
    return any(loc in t for loc in NSW_LOCATIONS)

# -----------------------------
# SCORING ENGINE
# -----------------------------
def score(item):
    text = item["title"].lower()
    price = item["price"]
    location = item["location"].lower()

    s = 0

    if any(k in text for k in KEYWORDS):
        s += 3

    if any(e in text for e in ENGINES):
        s += 3

    if PRICE_MIN <= price <= PRICE_MAX:
        s += 3
    else:
        s -= 2

    if is_nsw(text + location):
        s += 3
    else:
        s -= 3

    return s

# -----------------------------
# FAKE DATA STREAM (PLACEHOLDER)
# -----------------------------
def get_listings():
    return [
        {"title": "Hilux 2TR manual Sydney ute", "price": 3500, "location": "Sydney NSW"},
        {"title": "Prado 1GR Newcastle clean", "price": 4200, "location": "Newcastle NSW"},
        {"title": "Hilux hulx rough Canberra", "price": 1800, "location": "Canberra ACT"},
        {"title": "BMW broken car Melbourne", "price": 900, "location": "Melbourne VIC"}
    ]

# -----------------------------
# RUN SCAN CYCLE
# -----------------------------
def run_cycle():
    items = get_listings()

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
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        send(msg)

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    send("🤖 V5 Scanner Started (NSW + Canberra Mode)")

    while True:
        run_cycle()
        time.sleep(60)

if __name__ == "__main__":
    main()
