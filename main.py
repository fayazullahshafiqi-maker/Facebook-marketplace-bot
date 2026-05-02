def main():
    # SAFE TEXT STARTUP (always works)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": "🤖 V10 Started (Image + Link System Enabled)"
    })

    while True:
        run_cycle()
        time.sleep(60)
