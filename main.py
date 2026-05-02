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
# CATEGORIES (V16 CORE)
# -----------------------------
CATEGORIES = {
    "cars": ["hilux", "prado", "landcruiser", "dmax", "triton"],
    "parts": ["engine", "gearbox", "turbo", "diff"],
    "utes": ["ute", "tray", "dual cab"],
    "luxury": ["bmw", "mercedes", "audi"]
}

def detect_category(title):
    t = title.lower()

    for cat, keywords in CATEGORIES.items():
        for k in keywords:
            if k in t:
                return cat

    return "general"

# -----------------------------
# ID GENERATOR
# -----------------------------
def make_id(item):
    return hashlib.md5((item["title"] + item["location"]).lower().encode()).hexdigest()

# -----------------------------
# V16 INTELLIGENCE ENGINE
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    category = detect_category(title)

    score = 0
    reasons = []

    # -------------------------
    # CATEGORY LOGIC
    # -------------------------
    if category == "cars":
        if price < 4000:
            score += 5
            reasons.append("🔥 Cheap car deal")
        elif price < 7000:
            score += 3
            reasons.append("✔ Fair car price")

    elif category == "parts":
        if price < 500:
            score += 5
            reasons.append("🔥 Cheap parts deal")
        else:
            score += 2
            reasons.append("✔ Normal parts deal")

    elif category == "utes":
        if price < 5000:
            score += 4
            reasons.append("✔ Good ute deal")

    elif category == "luxury":
        score -= 2
        reasons.append("⚠ Luxury vehicle risk")

    else:
        score += 1
        reasons.append("ℹ General item")

    # -------------------------
    # KEYWORD BOOST
    # -------------------------
    if any(k in title for k in ["hilux", "prado", "engine", "gearbox"]):
        score += 2
        reasons.append("✔ High-value keyword match")

    return score, reasons, category

# -----------------------------
# PROCESS LISTING
# -----------------------------
def process(item):
    uid = make_id(item)

    if memory["seen"].get(uid):
        return

    s, reasons, category = score(item)

    if s < 5:
        return

    if s >= 7:
        tag = "🔥 HIGH PRIORITY DEAL"
    else:
        tag = "👍 GOOD DEAL"

    msg = f"""
{tag} ({s}/10) [{category.upper()}]

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
# WEBHOOK
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
    return "V16 MULTI-CATEGORY SYSTEM RUNNING"

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
