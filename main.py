import os
import requests
import time
import hashlib
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# -----------------------------
# NSW + CANBERRA SYSTEM
# -----------------------------
LOCATIONS = [
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
# MEMORY SYSTEM
# -----------------------------
seen_listings = set()
price_history = {}

# -----------------------------
# TELEGRAM
# -----------------------------
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -----------------------------
# UNIQUE ID
# -----------------------------
def make_id(item):
    raw = item["title"] + str(item["price"]) + item["location"]
    return hashlib.md5(raw.encode()).hexdigest()

# -----------------------------
# LOCATION CHECK
# -----------------------------
def is_valid_location(text):
    t = text.lower()
    return any(loc in t for loc in LOCATIONS)

# -----------------------------
# PRICE DROP CHECK
# -----------------------------
def check_price_drop(uid, current_price):
    old_price = price_history.get(uid)

    price_history[uid] = current_price

    if old_price and current_price < old_price:
        drop = old_price - current_price
        return True, drop

    return False, 0

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

    if is_valid_location(text + location):
        s += 3
    else:
        s -= 3

    return s

# -----------------------------
# DATA SOURCE (SIMULATION)
# -----------------------------
def get_listings():
    return [
        {"title": "Hilux 2TR manual Sydney ute", "price": 3500, "location": "Sydney NSW"},
        {"title": "Prado 1GR Newcastle clean", "price": 4200, "location": "Newcastle NSW"},
        {"title": "Hilux hulx rough Canberra", "price": 1800, "location": "Canberra ACT"},
        {"title": "BMW broken car Melbourne", "price": 900, "location": "Melbourne VIC"}
    ]

# -----------------------------
# MAIN LOOP
# -----------------------------
def run_cycle():
    global seen_listings

    items = get_listings()

    for i in items:

        uid = make_id(i)

        # ❌ skip duplicates
        if uid in seen_listings:
            continue

        s = score(i)

        if s >= 7:
            tag = "🔥 HOT NSW DEAL"
        elif s >= 5:
            tag = "👍 GOOD DEAL"
        else:
            continue

        # 📉 PRICE DROP LOGIC
        price_drop, drop_amount = check_price_drop(uid, i["price"])

        extra = ""
        if price_drop:
            extra = f"\n📉 PRICE DROPPED: -${drop_amount}"

        msg = f"""
{tag}{extra}

🚗 {i['title']}
📍 {i['location']}
💰 ${i['price']}
📊 Score: {s}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        send(msg)

        seen_listings.add(uid)

# -----------------------------
# LOOP ENGINE
# -----------------------------
def main():
    send("🤖 V6.1 Started (Clean + Price Drop Detection)")

    while True:
        run_cycle()
        time.sleep(60)

if __name__ == "__main__":
    main()
