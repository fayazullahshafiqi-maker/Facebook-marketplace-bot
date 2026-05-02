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
# MEMORY (V17 SELF-LEARNING)
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
# TARGETS
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
# CATEGORY DETECT
# -----------------------------
def detect(title):
    t = title.lower()

    for x in TARGETS:
        if x in t:
            return x

    return "general"

# -----------------------------
# SELF-LEARNING BOOST SYSTEM
# -----------------------------
def get_boost(keyword):
    return memory["likes"].get(keyword, 0)

# -----------------------------
# SCORE ENGINE (V17)
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    keyword = detect(title)

    score = 0
    reasons = []

    # -------------------------
    # BASE TARGET MATCH
    # -------------------------
    if keyword != "general":
        score += 2
        reasons.append(f"✔ Match: {keyword}")

    # -------------------------
    # SELF LEARNING BOOST
    # -------------------------
    boost = get_boost(keyword)

    if boost > 0:
        score += boost
        reasons.append(f"🧠 User interest boost (+{boost})")

    # -------------------------
    # PRICE LOGIC
    # -------------------------
    if price < 4000:
        score += 4
        reasons.append("🔥 Cheap deal")
    elif price < 7000:
        score += 2
        reasons.append("✔ Fair price")

    # -------------------------
    # RISK FILTER
    # -------------------------
    if "bmw" in title or "mercedes" in title:
        score -= 2
        reasons.append("⚠ Luxury risk")

    return score, reasons, keyword

# -----------------------------
# PROCESS ITEM
# -----------------------------
def process(item):
    uid = hashlib.md5((item["title"] + item["location"]).lower().encode()).hexdigest()

    if memory["seen"].get(uid):
        return

    s, reasons, keyword = score(item)

    if s < 5:
        return

    # simulate "learning"
    memory["likes"][keyword] = memory["likes"].get(keyword, 0) + 1

    tag = "🔥 HIGH PRIORITY" if s >= 7 else "👍 GOOD DEAL"

    msg = f"""
{tag} ({s}/10) [LEARNING: {keyword}]

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
# WEBHOOK
# -----------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json
    process(data)
    return {"status": "ok"}

# -----------------------------
# HEALTH
# -----------------------------
@app.route("/")
def home():
    return "V17 SELF-LEARNING ENGINE RUNNING"

# -----------------------------
# SIMULATOR
# -----------------------------
def simulator():
    time.sleep(10)

    while True:
        listing = {
            "title": "Toyota Hilux 2TR Sydney Clean Ute",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://facebook.com/marketplace/item/123"
        }

        try:
            requests.post(
                "http://127.0.0.1:8080/ingest",
                json=listing,
                timeout=10
            )
            print("SENT")

        except Exception as e:
            print("ERROR:", e)

        time.sleep(60)

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=simulator, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
