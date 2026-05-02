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
        return {"seen": {}, "price_map": {}}

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
# ID GENERATOR
# -----------------------------
def make_id(item):
    base = item["title"].lower().strip()
    return hashlib.md5(base.encode()).hexdigest()

# -----------------------------
# DATA
# -----------------------------
def get_listings():
    return [
        {"title": "Toyota Hilux 2TR Sydney clean ute", "price": 3500, "location": "Sydney NSW", "url": "link1"},
        {"title": "Toyota Hilux 2TR Sydney clean ute same repost", "price": 3200, "location": "Sydney NSW", "url": "link2"},
        {"title": "Prado 1GR Newcastle strong engine", "price": 4200, "location": "Newcastle NSW", "url": "link3"},
        {"title": "BMW broken engine car", "price": 900, "location": "Melbourne VIC", "url": "link4"},
    ]

# -----------------------------
# MARKET VALUE ESTIMATION
# -----------------------------
def expected_price(title):
    t = title.lower()

    if "hilux" in t:
        return 5000
    if "prado" in t:
        return 6500
    if "bmw" in t:
        return 2000
    return 4000

# -----------------------------
# SMART SCORING V11B
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    expected = expected_price(title)
    diff = expected - price

    score = 0
    reasons = []

    # VALUE CHECK
    if diff > 1500:
        score += 5
        reasons.append("🔥 Strong undervalued deal")
    elif diff > 500:
        score += 3
        reasons.append("✔ Slightly under market")
    else:
        score += 1
        reasons.append("⚠ Near market price")

    # MODEL QUALITY
    if "hilux" in title or "prado" in title:
        score += 3
        reasons.append("✔ High demand model")

    # RISK FILTER
    if "bmw" in title:
        score -= 2
        reasons.append("⚠ Risky vehicle type")

    return score, reasons

# -----------------------------
# FUZZY DUPLICATE CHECK
# -----------------------------
def is_duplicate(title):
    for seen in memory["seen"]:
        if title.lower()[:15] in seen:
            return True
    return False

# -----------------------------
# LOOP
# -----------------------------
def run_cycle():
    print("V11B RUNNING...")

    items = get_listings()

    for i in items:
        uid = make_id(i)

        if memory["seen"].get(uid):
            continue

        if is_duplicate(i["title"]):
            print("SKIP DUPLICATE:", i["title"])
            continue

        s, reasons = score(i)

        print("CHECK:", i["title"], s)

        if s < 5:
            continue

        if s >= 7:
            tag = "🔥 HIGH PRIORITY DEAL"
        else:
            tag = "👍 GOOD DEAL"

        msg = f"""
{tag} (Score: {s}/10)

🚗 {i['title']}
📍 {i['location']}
💰 ${i['price']}

📊 WHY:
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
    send("🤖 V11B MARKET INTELLIGENCE STARTED")

    while True:
        run_cycle()
        time.sleep(30)

if __name__ == "__main__":
    main()
