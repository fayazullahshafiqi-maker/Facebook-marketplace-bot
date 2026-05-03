import os
import requests
from scraper import scrape_marketplace

# Railway will inject PORT automatically (keep for safety if you expand later)
PORT = int(os.environ.get("PORT", 8000))

# Your Railway ingest URL (IMPORTANT: must include https://)
INGEST_URL = os.environ.get(
    "INGEST_URL",
    "https://facebook-marketplace-bot-production-f538.up.railway.app"
)

def send_to_ingest(item):
    try:
        response = requests.post(INGEST_URL, json=item, timeout=10)
        print("SENT:", item, "STATUS:", response.status_code)
    except Exception as e:
        print("FAILED TO SEND:", item, "ERROR:", str(e))


def run_scanner():
    print("🚀 Starting Marketplace Scanner...")

    listings = scrape_marketplace()

    if not listings:
        print("⚠️ No listings found")
        return

    for item in listings:
        send_to_ingest(item)


if __name__ == "__main__":
    run_scanner()
