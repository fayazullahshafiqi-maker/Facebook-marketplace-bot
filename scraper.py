from playwright.sync_api import sync_playwright

KEYWORDS = [
    "toyota rav4",
    "rav4",
    "toyota kluger",
    "kluger",
    "toyota prado",
    "prado",
    "toyota hilux",
    "hilux",
    "isuzu d-max",
    "dmax",
    "d-max",
    "toyota hiace",
    "hiace"
]


def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for keyword in KEYWORDS:

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            # scroll to load listings
            for _ in range(3):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(3000)

            # grab visible content blocks
            items = page.query_selector_all("div")

            for item in items:
                try:
                    text = item.inner_text()

                    if not text or len(text) < 20:
                        continue

                    if any(k.lower() in text.lower() for k in KEYWORDS):

                        results.append({
                            "title": text[:120],
                            "price": 0,
                            "location": "NSW",
                            "url": page.url
                        })

                    if len(results) >= 20:
                        break

                except:
                    continue

        browser.close()

    return results
