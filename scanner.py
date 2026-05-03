import os
import requests
from scraper import scrape_marketplace

INGEST_URL = os.environ.get(
    "INGEST_URL",
    "https://facebook-marketplace-bot-production-f538.up.railway.app"
)

def send(item):
    try:
        r = requests.post(INGEST_URL, json=item, timeout=10)
        print("SENT:", item, "STATUS:", r.status_code)
    except Exception as e:
        print("SEND FAILED:", item, "ERROR:", str(e))


def run():
    print("🚀 Scanner starting...")

    try:
        listings = scrape_marketplace()
    except Exception as e:
        print("SCRAPER ERROR:", str(e))
        return

    if not listings:
        print("⚠️ No listings found")
        return

    for item in listings:
        send(item)

    print("✅ Scan complete")


if __name__ == "__main__":
    run()
