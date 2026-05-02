import os
import json
import hashlib
import requests
import time
from datetime import datetime
from flask import Flask, request
from threading import Thread

app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

INGEST_URL = ""  # NOT USED (internal system)

MEMORY_FILE = "memory.json"

# -----------------------------
# MEMORY SYSTEM
# -----------------------------
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"seen": {}, "likes": {}}

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
TARGETS = ["hilux", "prado", "landcruiser", "engine", "gearbox", "ute"]

def detect(title):
    t = title.lower()
    for x in TARGETS:
        if x in t:
            return x
    return "general"

# -----------------------------
# SCORING ENGINE
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    keyword = detect(title)

    s = 0
    reasons = []

    if keyword != "general":
        s += 2
        reasons.append(f"✔ Match: {keyword}")

    s += memory["likes"].get(keyword, 0)

    if price < 4000:
        s += 4
        reasons.append("🔥 Cheap deal")
    elif price < 7000:
        s += 2
        reasons.append("✔ Fair price")

    if "bmw" in title or "mercedes" in title:
        s -= 2
        reasons.append("⚠ Luxury risk")

    return s, reasons, keyword

# -----------------------------
# PROCESS LISTING
# -----------------------------
def process(item):
    uid = hashlib.md5((item["title"] + item["location"]).lower().encode()).hexdigest()

    if memory["seen"].get(uid):
        return

    s, reasons, keyword = score(item)

    if s < 5:
        return

    memory["likes"][keyword] = memory["likes"].get(keyword, 0) + 1

    tag = "🔥 HIGH PRIORITY" if s >= 7 else "👍 GOOD DEAL"

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
# INGEST API
# -----------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json
    process(data)
    return {"status": "ok"}

@app.route("/")
def home():
    return "V21 FINAL SYSTEM RUNNING"

# -----------------------------
# INTERNAL COLLECTORS (RUN INSIDE SAME APP)
# -----------------------------
def collector_hilux():
    while True:
        data = {
            "title": "Toyota Hilux 2TR Clean Ute Sydney",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/111"
        }
        try:
            requests.post("http://127.0.0.1:8080/ingest", json=data)
        except:
            pass
        time.sleep(60)

def collector_engine():
    while True:
        data = {
            "title": "Toyota 1KD Engine Good Condition",
            "price": 900,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/222"
        }
        try:
            requests.post("http://127.0.0.1:8080/ingest", json=data)
        except:
            pass
        time.sleep(90)

def collector_parts():
    while True:
        data = {
            "title": "Toyota Gearbox Auto 4x4",
            "price": 600,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/333"
        }
        try:
            requests.post("http://127.0.0.1:8080/ingest", json=data)
        except:
            pass
        time.sleep(120)

# -----------------------------
# START EVERYTHING
# -----------------------------
if __name__ == "__main__":
    Thread(target=collector_hilux).start()
    Thread(target=collector_engine).start()
    Thread(target=collector_parts).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
