import os
import json
import hashlib
import requests
import time
import threading
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

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
        return {
            "seen": {},
            "likes": {}
        }

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
# TARGET SYSTEM
# -----------------------------
TARGETS = [
    "hilux",
    "prado",
    "landcruiser",
    "dmax",
    "triton",
    "engine",
    "gearbox",
    "ute"
]

# -----------------------------
# DETECT CATEGORY
# -----------------------------
def detect(title):
    t = title.lower()

    for x in TARGETS:
        if x in t:
            return x

    return "general"

# -----------------------------
# MEMORY BOOST
# -----------------------------
def boost(keyword):
    return memory["likes"].get(keyword, 0)

# -----------------------------
# INTELLIGENCE ENGINE (V17 CORE)
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    keyword = detect(title)

    score = 0
    reasons = []

    if keyword != "general":
        score += 2
        reasons.append(f"✔ Match: {keyword}")

    score += boost(keyword)

    if price < 4000:
        score += 4
        reasons.append("🔥 Cheap deal")
    elif price < 7000:
        score += 2
        reasons.append("✔ Fair price")

    if "bmw" in title or "mercedes" in title:
        score -= 2
        reasons.append("⚠ Luxury risk")

    return score, reasons, keyword

# -----------------------------
# PROCESS ENGINE
# -----------------------------
def process(item):
    uid = hashlib.md5((item["title"] + item["location"]).lower().encode()).hexdigest()

    if memory["seen"].get(uid):
        return

    s, reasons, keyword = score(item)

    if s < 5:
        return

    # self-learning boost
    memory["likes"][keyword] = memory["likes"].get(keyword, 0) + 1

    tag = "🔥 HIGH PRIORITY" if s >= 7 else "👍 GOOD DEAL"

    msg = f"""
{tag} ({s}/10) [COLLECTED: {keyword}]

🚗 {item['title']}
📍 {item['location']}
💰 ${item['price']}

📊 WHY:
{chr(10).join(reasons)}

🧠 Interest Level: {memory['likes'][keyword]}
🔗 {item['url']}
⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    send(msg)

    memory["seen"][uid] = True
    save_memory(memory)

# -----------------------------
# WEBHOOK (INGEST ENTRY POINT)
# -----------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json
    process(data)
    return {"status": "ok"}

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.route("/")
def home():
    return "V18B MULTI-COLLECTOR SYSTEM RUNNING"

# -----------------------------
# COLLECTOR 1 (SIMULATED HILUX FEED)
# -----------------------------
def collector_hilux():
    while True:
        time.sleep(30)

        listing = {
            "title": "Toyota Hilux 2TR Sydney Clean Ute",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://facebook.com/marketplace/item/123"
        }

        requests.post("http://127.0.0.1:8080/ingest", json=listing)
        print("HILUX COLLECTOR SENT")

# -----------------------------
# COLLECTOR 2 (ENGINE FEED)
# -----------------------------
def collector_engine():
    while True:
        time.sleep(45)

        listing = {
            "title": "Toyota 1KD Engine Good Condition",
            "price": 900,
            "location": "Sydney NSW",
            "url": "https://facebook.com/marketplace/item/999"
        }

        requests.post("http://127.0.0.1:8080/ingest", json=listing)
        print("ENGINE COLLECTOR SENT")

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=collector_hilux, daemon=True).start()
    threading.Thread(target=collector_engine, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
