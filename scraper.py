import requests
from bs4 import BeautifulSoup

def scrape_marketplace(query):
    url = f"https://www.facebook.com/marketplace/sydney/search?query={query.replace(' ', '%20')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []

    # find all links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)

        if "/marketplace/item/" in href or "marketplace" in href:
            if text and len(text) > 10:
                results.append({
                    "title": text,
                    "url": href,
                    "price": 0,
                    "location": "Sydney"
                })

    # remove duplicates
    seen = set()
    clean = []

    for r in results:
        if r["url"] not in seen:
            clean.append(r)
            seen.add(r["url"])

    return clean[:20]
