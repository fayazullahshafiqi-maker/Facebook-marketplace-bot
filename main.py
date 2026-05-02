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
# MEMORY
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
def send_photo(item, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": item["image"],
        "caption": caption
    })
    print(r.text)

def send_text(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -----------------------------
# ID
# -----------------------------
def make_id(item):
    return hashlib.md5((item["title"] + item["location"]).encode()).hexdigest()

# -----------------------------
# DATA (SIMULATED)
# -----------------------------
def get_listings():
    return [
        {
            "title": "Hilux 2TR Sydney ute clean",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://www.facebook.com/marketplace/item/111",
            "image": "https://via.placeholder.com/600x400.png?text=Hilux+Sydney"
        },
        {
            "title": "Prado 1GR Newcastle strong",
            "price": 4200,
            "location": "Newcastle NSW",
            "url": "https://www.facebook.com/marketplace/item/222",
            "image": "https://via.placeholder.com/600x400.png?text=Prado+Newcastle"
        },
        {
            "title": "Hilux Canberra rough ute",
            "price": 1800,
            "location": "Canberra ACT",
            "url": "https://www.facebook.com/marketplace/item/333",
            "image": "https://via.placeholder.com/600x400.png?text=Hilux+Canberra"
        }
    ]

# -----------------------------
# SCORE (SIMPLIFIED so it WORKS)
# -----------------------------
def score(item):
    price = item["price"]

    if price < 5000:
        return 8
    elif price < 8000:
        return 6
    else:
        return 4

# -----------------------------
# PRICE DROP CHECK
# -----------------------------
def check_price_drop(uid, price):
    old = memory["prices"].get(uid)
    memory["prices"][uid] = price

    if old and price < old:
        return True, old - price

    return False, 0

# -----------------------------
# MAIN LOOP
# -----------------------------
def run_cycle():
    items = get_listings()

    for i in items:
        uid = make_id(i)

        if memory["seen"].get(uid):
            continue

        s = score(i)

        # IMPORTANT: LOWERED THRESHOLD so you SEE results
        if s >= 4:
            tag = "🔥 DEAL ALERT"
        else:
            continue

        dropped, amount = check_price_drop(uid, i["price"])

        extra = ""
        if dropped:
            extra = f"\n📉 PRICE DROPPED: -${amount}"

        caption = f"""
<b>{tag}</b>
{extra}

🚗 {i['title']}
📍 {i['location']}
💰 ${i['price']}
📊 Score: {s}

🔗 {i['url']}
⏰ {datetime.now().strftime('%H:%M:%S')}
"""

        send_photo(i, caption)

        memory["seen"][uid] = True

    save_memory(memory)

# -----------------------------
# STARTUP + LOOP
# -----------------------------
def main():
    send_text("🤖 V10 Running (FIXED + Guaranteed Output Mode)")

    while True:
        run_cycle()
        time.sleep(60)

if __name__ == "__main__":
    main()
