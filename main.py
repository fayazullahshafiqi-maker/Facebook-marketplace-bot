from flask import Flask, jsonify

app = Flask(__name__)

# simple health check
@app.route("/")
def home():
    return "Marketplace bot is running"

# fake scan endpoint (we will upgrade scraper next)
@app.route("/scan")
def scan():
    try:
        results = scrape_marketplace()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)})


# import at bottom to avoid circular issues
from scraper import scrape_marketplace


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
