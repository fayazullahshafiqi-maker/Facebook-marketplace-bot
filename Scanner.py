import time
import random
import requests

INGEST_URL = "http://127.0.0.1:8080/ingest"

KEYWORDS = [
    "Hilux 2TR single cab manual",
    "Hilux 3RZ single cab",
    "1GR Landcruiser single cab",
    "1KD Prado",
    "1GR Prado"
]

LOCATIONS = [
    "Sydney NSW",
    "Parramatta NSW",
    "Auburn NSW",
    "Canberra ACT"
]

def generate_listing(keyword):
    return {
        "title": keyword,
        "price": random.randint(2000, 9000),
        "location": random.choice(LOCATIONS),
        "url": "https://example.com/listing"
    }

while True:
    for kw in KEYWORDS:

        listing = generate_listing(kw)

        try:
            requests.post(INGEST_URL, json=listing)
            print("SENT:", listing)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(15)
