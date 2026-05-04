from playwright.sync_api import sync_playwright

KEYWORDS = [
    "rav4", "kluger", "prado", "hilux", "dmax", "d-max", "hiace"
]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for keyword in KEYWORDS:

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword}"

            page.goto(url, timeout=60000)
            page.wait_for_timeout(6000)

            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(3000)

            # ONLY TARGET LINKS (better than div spam)
            items = page.query_selector_all("a")

            for item in items:
                try:
                    text = item.inner_text()

                    if not text or len(text) < 15:
                        continue

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
