import os
import requests
import time
import hashlib
import json
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

MEMORY_FILE = "memory.json"

# -----------------------------
# LOCATIONS (NSW + CANBERRA)
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
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"seen": {}, "prices": {}}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

memory = load_memory()

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
    raw = item["title"] + item["location"]
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
def check_price_drop(uid, price):
    old_price = memory["prices"].get(uid)
    memory["prices"][uid] = price

    if old_price and price < old_price:
        return True, old_price - price

    return False, 0

# -----------------------------
# SCORING ENGINE (UNCHANGED)
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
# V9 DATA LAYER (WITH URL)
# -----------------------------
def ingest_data(source="simulated_v9"):
    return [
        {
            "id": "1",
            "title": "Hilux 2TR manual Sydney ute",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://www.facebook.com/marketplace/item/111",
            "source": source
        },
        {
            "id": "2",
            "title": "Prado 1GR Newcastle clean",
            "price": 4200,
            "location": "Newcastle NSW",
            "url": "https://www.facebook.com/marketplace/item/222",
            "source": source
        },
        {
            "id": "3",
            "title": "Hilux rough Canberra ute",
            "price": 1800,
            "location": "Canberra ACT",
            "url": "https://www.facebook.com/marketplace/item/333",
            "source": source
        },
        {
            "id": "4",
            "title": "BMW broken car Melbourne",
            "price": 900,
            "location": "Melbourne VIC",
            "url": "https://www.facebook.com/marketplace/item/444",
            "source": source
        }
    ]

# -----------------------------
# MAIN ENGINE
# -----------------------------
def run_cycle():
    items = ingest_data()

    for i in items:
        uid = make_id(i)

        if memory["seen"].get(uid):
            continue

        s = score(i)

        if s >= 7:
            tag = "🔥 HOT NSW DEAL"
        elif s >= 5:
            tag = "👍 GOOD DEAL"
        else:
            continue

        dropped, amount = check_price_drop(uid, i["price"])

        extra = ""
        if dropped:
            extra = f"\n📉 PRICE DROPPED: -${amount}"

        msg = f"""
{tag}{extra}

🚗 {i['title']}
📍 {i['location']}
💰 ${i['price']}
🔗 {i['url']}
📊 Score: {s}
🌐 Source: {i['source']}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        send(msg)

        memory["seen"][uid] = True

    save_memory(memory)

# -----------------------------
# LOOP
# -----------------------------
def main():
    send("🤖 V9 Started (HTTPS Link System Enabled)")

    while True:
        run_cycle()
        time.sleep(60)

if __name__ == "__main__":
    main()
