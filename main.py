import os
from flask import Flask, request
import requests

from negotiation import calculate_offer, generate_message

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

PROFIT_RULES = {
    "2tr": 5000,
    "3rz": 4800,
    "1gr_single": 8000,
    "1gr_prado": 4000,
    "1kd_prado": 6000
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def detect_model(title):
    t = title.lower()

    if "2tr" in t:
        return "2tr"

    if "3rz" in t:
        return "3rz"

    if "1gr" in t and "prado" not in t:
        return "1gr_single"

    if "1gr" in t and "prado" in t:
        return "1gr_prado"

    if "1kd" in t:
        return "1kd_prado"

    return None

@app.route("/ingest", methods=["POST"])
def ingest():

    item = request.json

    title = item["title"]
    price = item["price"]
    location = item["location"]

    model = detect_model(title)

    if not model:
        return {"status": "ignored"}

    offer = calculate_offer(price)

    msg = f"""
🔥 DEAL FOUND

🚗 {title}
📍 {location}
💰 Listed: ${price}
🤝 Suggested Offer: ${offer}

📩 MESSAGE:
{generate_message(title, offer)}

🔗 {item["url"]}
"""

    send_telegram(msg)

    return {"status": "sent"}

@app.route("/")
def home():
    return "V24 BOT RUNNING"

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(host="0.0.0.0", port=port)
