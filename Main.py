import requests

BOT_TOKEN = "7862438221:AAFQ12XjSJOp8Kk5x5erFmVC4OWc0HzYRv8"
CHAT_ID = "7403593902"

def send_test():

    msg = "🤖 Bot is running successfully (NSW system connected)"

    requests.post(

        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",

        data={"chat_id": CHAT_ID, "text": msg}

    )

send_test()
