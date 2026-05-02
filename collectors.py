import requests
import time
from threading import Thread

INGEST_URL = "http://127.0.0.1:8080/ingest"

# -----------------------------
# HILUX COLLECTOR
# -----------------------------
def collector_hilux():
    while True:
        data = {
            "title": "Toyota Hilux 2TR Clean Ute Sydney",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/111"
        }

        requests.post(INGEST_URL, json=data)
        print("HILUX SENT")

        time.sleep(30)

# -----------------------------
# ENGINE COLLECTOR
# -----------------------------
def collector_engine():
    while True:
        data = {
            "title": "Toyota 1KD Engine Good Condition",
            "price": 900,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/222"
        }

        requests.post(INGEST_URL, json=data)
        print("ENGINE SENT")

        time.sleep(45)

# -----------------------------
# PARTS COLLECTOR
# -----------------------------
def collector_parts():
    while True:
        data = {
            "title": "Toyota Gearbox Auto 4x4",
            "price": 600,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/333"
        }

        requests.post(INGEST_URL, json=data)
        print("PARTS SENT")

        time.sleep(60)

# -----------------------------
# RUN ALL COLLECTORS
# -----------------------------
if __name__ == "__main__":
    Thread(target=collector_hilux).start()
    Thread(target=collector_engine).start()
    Thread(target=collector_parts).start()

    while True:
        time.sleep(9999)
