import os
import json
import hashlib
import requests
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
TARGETS = ["hilux", "prado", "engine", "gearbox", "ute"]

def detect(title):
    t = title.lower()
    for x in TARGETS:
        if x in t:
            return x
    return "general"

# -----------------------------
# SCORE ENGINE
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
# PROCESS
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
# WEBHOOK
# -----------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json
    process(data)
    return {"status": "ok"}

@app.route("/")
def home():
    return "V20A SYSTEM RUNNING"

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
