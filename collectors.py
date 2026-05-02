import requests
import time
import os

# Must be set in Railway environment variables
INGEST_URL = os.environ.get("INGEST_URL")

# -----------------------------
# SAFETY CHECK
# -----------------------------
if not INGEST_URL:
    raise ValueError("INGEST_URL is not set in environment variables")

# -----------------------------
# MAIN CLOUD COLLECTOR LOOP
# -----------------------------
def run_collector():
    while True:
        listing = {
            "title": "Toyota Hilux 2TR Clean Ute Sydney",
            "price": 3500,
            "location": "Sydney NSW",
            "url": "https://facebook.com/item/111"
        }

        try:
            response = requests.post(INGEST_URL, json=listing, timeout=10)

            if response.status_code == 200:
                print("✅ SENT TO CLOUD BOT")
            else:
                print("⚠️ FAILED:", response.status_code)

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(60)

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    run_collector()
