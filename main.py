import os
import requests

# Get secrets safely from Railway (NOT from code)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def main():
    send_message("🤖 Bot is running successfully (NSW system connected)")

if __name__ == "__main__":
    main()
