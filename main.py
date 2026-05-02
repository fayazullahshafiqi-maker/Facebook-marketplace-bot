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
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -----------------------------
# ID
# -----------------------------
def make_id(item):
    return hashlib.md5((item["title"] + item["location"]).lower().encode()).hexdigest()

# -----------------------------
# DATA (SIMULATED)
# -----------------------------
def get_listings():
    return [
        {
            "title": "Toyota Hilux 2TR manual clean",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://facebook.com/marketplace/item/111"
        },
        {
            "title": "Toyota Prado 1GR strong engine",
            "price": 4200,
            "location": "Newcastle NSW",
            "url": "https://facebook.com/marketplace/item/222"
        },
        {
            "title": "Hilux rough ute Canberra",
            "price": 1800,
            "location": "Canberra ACT",
            "url": "https://facebook.com/marketplace/item/333"
        },
        {
            "title": "BMW broken engine car",
            "price": 900,
            "location": "Melbourne VIC",
            "url": "https://facebook.com/marketplace/item/444"
        }
    ]

# -----------------------------
# SMART SCORING ENGINE (V11A)
# -----------------------------
def score(item):
    text = item["title"].lower()
    price = item["price"]

    score = 0
    reasons = []

    # MODEL VALUE
    if "hilux" in text or "prado" in text:
        score += 4
        reasons.append("✔ High demand model")

    # ENGINE VALUE
    if "2tr" in text or "1gr" in text:
        score += 3
        reasons.append("✔ Strong engine type")

    # PRICE LOGIC
    if price < 2500:
        score += 4
        reasons.append("✔ Very cheap deal")
    elif price < 5000:
        score += 3
        reasons.append("✔ Under market value")
    elif price < 8000:
        score += 1
        reasons.append("⚠ Slightly high")

    # PENALTY
    if "bmw" in text:
        score -= 2
        reasons.append("⚠ Risky model")

    return score, reasons

# -----------------------------
# LOOP
# -----------------------------
def run_cycle():
    print("V11A RUNNING...")

    items = get_listings()

    for i in items:
        uid = make_id(i)

        if memory["seen"].get(uid):
            continue

        s, reasons = score(i)

        print("CHECK:", i["title"], s)

        # FILTER (SMART)
        if s < 5:
            continue

        msg = f"""
🔥 DEAL ALERT (Score: {s}/10)

🚗 {i['title']}
📍 {i['location']}
💰 ${i['price']}

📊 WHY THIS DEAL:
{chr(10).join(reasons)}

🔗 {i['url']}
⏰ {datetime.now().strftime('%H:%M:%S')}
"""

        send(msg)

        memory["seen"][uid] = True

    save_memory(memory)

# -----------------------------
# START
# -----------------------------
def main():
    send("🤖 V11A SMART INTELLIGENCE STARTED")

    while True:
        run_cycle()
        time.sleep(30)

if __name__ == "__main__":
    main()
