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

MIN_PRICE = 200
MAX_PRICE = 18000


def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for keyword in KEYWORDS:

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            # Scroll to load listings
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(3000)

            page.mouse.wheel(0, 6000)
            page.wait_for_timeout(3000)

            # Try to capture listing links
            items = page.query_selector_all("a")

            for item in items[:30]:
                try:
                    text = item.inner_text()

                    if not text:
                        continue

                    if any(k.lower() in text.lower() for k in KEYWORDS):

                        results.append({
                            "title": text[:120],
                            "price": 0,
                            "location": "NSW",
                            "url": "https://facebook.com" + (item.get_attribute("href") or "")
                        })

                except:
                    continue

        browser.close()

    return results
