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
        return {"seen": {}}

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
    raw = (item["title"] + item["location"]).lower()
    return hashlib.md5(raw.encode()).hexdigest()

# -----------------------------
# INBOX (DATA INPUT LAYER)
# -----------------------------
def get_incoming_listings():
    """
    THIS IS YOUR FUTURE ENTRY POINT.

    Later you will replace this with:
    - Facebook API
    - webhook
    - scraper
    - database pull
    """

    # TEMP SIMULATION ONLY
    return [
        {
            "title": "Toyota Hilux 2TR clean ute Sydney",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/111"
        },
        {
            "title": "Prado 1GR strong engine Newcastle",
            "price": 4200,
            "location": "Newcastle NSW",
            "url": "https://facebook.com/item/222"
        },
        {
            "title": "BMW broken car Melbourne",
            "price": 900,
            "location": "Melbourne VIC",
            "url": "https://facebook.com/item/333"
        }
    ]

# -----------------------------
# MARKET VALUE MODEL (simple baseline)
# -----------------------------
def market_value(title):
    t = title.lower()

    if "hilux" in t:
        return 5000
    if "prado" in t:
        return 6500
    if "bmw" in t:
        return 2000

    return 4000

# -----------------------------
# INTELLIGENCE ENGINE (V11 LOGIC INSIDE)
# -----------------------------
def analyze(item):
    title = item["title"].lower()
    price = item["price"]

    expected = market_value(title)
    gap = expected - price

    score = 0
    reasons = []

    # VALUE CHECK
    if gap > 2000:
        score += 5
        reasons.append("🔥 Extremely undervalued")
    elif gap > 800:
        score += 3
        reasons.append("✔ Under market price")
    else:
        score += 1
        reasons.append("⚠ Near market value")

    # MODEL BOOST
    if "hilux" in title or "prado" in title:
        score += 3
        reasons.append("✔ High demand model")

    # RISK FILTER
    if "bmw" in title:
        score -= 2
        reasons.append("⚠ Risky vehicle type")

    return score, reasons

# -----------------------------
# PROCESS ENGINE
# -----------------------------
def run_cycle():
    print("V12A RUNNING...")

    listings = get_incoming_listings()

    for item in listings:
        uid = make_id(item)

        if memory["seen"].get(uid):
            continue

        score, reasons = analyze(item)

        print("ANALYZING:", item["title"], score)

        if score < 5:
            continue

        if score >= 7:
            tag = "🔥 HIGH PRIORITY DEAL"
        else:
            tag = "👍 GOOD DEAL"

        msg = f"""
{tag} (Score: {score}/10)

🚗 {item['title']}
📍 {item['location']}
💰 ${item['price']}

📊 WHY:
{chr(10).join(reasons)}

🔗 {item['url']}
⏰ {datetime.now().strftime('%H:%M:%S')}
"""

        send(msg)

        memory["seen"][uid] = True

    save_memory(memory)

# -----------------------------
# START
# -----------------------------
def main():
    send("🤖 V12A INGESTION ENGINE STARTED")

    while True:
        run_cycle()
        time.sleep(30)

if __name__ == "__main__":
    main()
