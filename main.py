from flask import Flask, jsonify
from scraper import scrape_marketplace

app = Flask(__name__)

@app.route("/")
def home():
    return "Marketplace bot is running"

@app.route("/scrape")
def scrape():
    data = scrape_marketplace()
    return jsonify(data)

@app.route("/api")
def api():
    data = scrape_marketplace()
    return jsonify({
        "count": len(data),
        "results": data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
