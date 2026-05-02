import os
import json
import hashlib
import requests
import threading
import time
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# IMPORTANT:
# Replace with your Railway public URL later if needed
BASE_URL = os.environ.get("RAILWAY_PUBLIC_DOMAIN")

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

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# -----------------------------
# ID
# -----------------------------
def make_id(item):
    raw = (item["title"] + item["location"]).lower()
    return hashlib.md5(raw.encode()).hexdigest()

# -----------------------------
# SCORING
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    s = 0
    reasons = []

    if "hilux" in title or "prado" in title:
        s += 4
        reasons.append("✔ High demand model")

    if price < 4000:
        s += 4
        reasons.append("🔥 Under market price")
    elif price < 7000:
        s += 2
        reasons.append("✔ Fair deal")

    if "bmw" in title:
        s -= 2
        reasons.append("⚠ Risk vehicle")

    return s, reasons

# -----------------------------
# PROCESS
# -----------------------------
def process(item):
    uid = make_id(item)

    if memory["seen"].get(uid):
        return

    s, reasons = score(item)

    if s < 5:
        return

    msg = f"""
🔥 LIVE DEAL ALERT ({s}/10)

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
    return "V14A LIVE INGESTION ENGINE ACTIVE"

# -----------------------------
# LIVE INGESTION SIMULATOR
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
                f"https://{BASE_URL}/ingest",
                json=listing,
                timeout=10
            )

            print("SIMULATED LISTING SENT")

        except Exception as e:
            print("SIMULATOR ERROR:", e)

        time.sleep(60)

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=simulator, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))

    app.run(host="0.0.0.0", port=port)
