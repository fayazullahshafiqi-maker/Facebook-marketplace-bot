import os
import json
import hashlib
from flask import Flask, request
import requests
from datetime import datetime

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
# ID
# -----------------------------
def make_id(item):
    raw = (item["title"] + item["location"]).lower()
    return hashlib.md5(raw.encode()).hexdigest()

# -----------------------------
# SMART SCORE (V12 LOGIC)
# -----------------------------
def score(item):
    title = item["title"].lower()
    price = item["price"]

    score = 0
    reasons = []

    if "hilux" in title or "prado" in title:
        score += 4
        reasons.append("✔ High demand model")

    if price < 4000:
        score += 4
        reasons.append("🔥 Under market price")
    elif price < 7000:
        score += 2
        reasons.append("✔ Fair deal")

    if "bmw" in title:
        score -= 2
        reasons.append("⚠ Risk vehicle")

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

    msg = f"""
🔥 DEAL ALERT (Score {s}/10)

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
# WEBHOOK ENDPOINT (THIS IS V13 CORE)
# -----------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json

    print("RECEIVED:", data)

    process(data)

    return {"status": "ok"}

# -----------------------------
# STARTUP
# -----------------------------
@app.route("/")
def home():
    return "V13 INGESTION ENGINE RUNNING"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
