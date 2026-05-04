from flask import Flask, jsonify
from scraper import scrape_marketplace

app = Flask(__name__)

@app.route("/")
def home():
    return "Marketplace bot is running"

@app.route("/scan")
def scan():
    try:
        data = scrape_marketplace()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
