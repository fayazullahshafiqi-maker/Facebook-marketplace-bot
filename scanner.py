import os
import requests
from scraper import scrape_marketplace

INGEST_URL = os.environ.get("INGEST_URL")

def send(item):
    try:
        r = requests.post(INGEST_URL, json=item, timeout=10)
        print("SENT:", item)
    except Exception as e:
        print("SEND ERROR:", e)

def run():
    print("🚀 Scanner running...")

    listings = scrape_marketplace()

    for item in listings:
        send(item)

if __name__ == "__main__":
    run()
