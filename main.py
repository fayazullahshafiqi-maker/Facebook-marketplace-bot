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
# TARGET SYSTEM (V15A CORE)
# -----------------------------
TARGETS = [
    "hilux",
    "prado",
    "landcruiser",
    "dmax",
    "triton",
    "ute",
    "engine",
    "gearbox"
]

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
# ID
# -----------------------------
def make_id(item):
    return hashlib.md5((item["title"] + item["location"]).lower().encode()).hexdigest()

# -----------------------------
# V15A SMART SCORING ENGINE
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    score = 0
    reasons = []

    # -------------------------
    # TARGET MATCHING
    # -------------------------
    matched = False
    for t in TARGETS:
        if t in title:
            score += 3
            reasons.append(f"✔ Target match: {t}")
            matched = True

    if not matched:
        score -= 2
        reasons.append("⚠ No target match")

    # -------------------------
    # PRICE LOGIC
    # -------------------------
    if price < 4000:
        score += 4
        reasons.append("🔥 Very cheap deal")
    elif price < 7000:
        score += 2
        reasons.append("✔ Fair price")
    else:
        reasons.append("⚠ High price")

    # -------------------------
    # RISK FILTER
    # -------------------------
    if "bmw" in title or "mercedes" in title:
        score -= 2
        reasons.append("⚠ Luxury risk vehicle")

    return score, reasons

# -----------------------------
# PROCESS LISTING
# -----------------------------
def process(item):
    uid = make_id(item)

    if memory["seen"].get(uid):
        return

    s, reasons = score(item)

    if s < 5:
        return

    if s >= 7:
        tag = "🔥 HIGH PRIORITY DEAL"
    else:
        tag = "👍 GOOD DEAL"

    msg = f"""
{tag} ({s}/10)

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
# WEBHOOK ENDPOINT
# -----------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json
    print("RECEIVED:", data)

    process(data)

    return {"status": "ok"}

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.route("/")
def home():
    return "V15A TARGET SYSTEM RUNNING"

# -----------------------------
# SIMULATOR (TESTING ONLY)
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
            print("SIMULATED LISTING SENT")

        except Exception as e:
            print("ERROR:", e)

        time.sleep(60)

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=simulator, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
