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
# TELEGRAM (TEXT ONLY - SAFE)
# -----------------------------
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print("SEND:", r.text)

# -----------------------------
# ID
# -----------------------------
def make_id(item):
    return hashlib.md5((item["title"] + item["location"]).encode()).hexdigest()

# -----------------------------
# DATA (SIMULATED)
# -----------------------------
def get_listings():
    return [
        {
            "title": "Hilux 2TR Sydney ute clean",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://www.facebook.com/marketplace/item/111"
        },
        {
            "title": "Prado 1GR Newcastle strong",
            "price": 4200,
            "location": "Newcastle NSW",
            "url": "https://www.facebook.com/marketplace/item/222"
        },
        {
            "title": "Hilux Canberra rough ute",
            "price": 1800,
            "location": "Canberra ACT",
            "url": "https://www.facebook.com/marketplace/item/333"
        }
    ]

# -----------------------------
# SIMPLE SCORE (FOR TESTING)
# -----------------------------
def score(item):
    if item["price"] < 5000:
        return 8
    return 5

# -----------------------------
# LOOP
# -----------------------------
def run_cycle():
    print("RUNNING CYCLE...")

    items = get_listings()

    for i in items:
        uid = make_id(i)

        if memory["seen"].get(uid):
            continue

        s = score(i)

        print("FOUND:", i["title"], "score:", s)

        if s >= 5:
            tag = "🔥 DEAL ALERT"
        else:
            continue

        msg = f"""
{tag}

🚗 {i['title']}
📍 {i['location']}
💰 ${i['price']}
📊 Score: {s}

🔗 {i['url']}
⏰ {datetime.now().strftime('%H:%M:%S')}
"""

        send_message(msg)

        memory["seen"][uid] = True

    save_memory(memory)

# -----------------------------
# START
# -----------------------------
def main():
    send_message("🤖 C10 CLEAN MODE STARTED (TEXT + LINK ONLY)")

    while True:
        run_cycle()
        time.sleep(30)

if __name__ == "__main__":
    main()
