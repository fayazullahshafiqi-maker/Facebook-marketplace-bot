from playwright.sync_api import sync_playwright

KEYWORDS = [
    "rav4", "kluger", "prado", "hilux", "hiace", "dmax", "d-max"
]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        url = "https://www.facebook.com/marketplace/sydney/search/?query=toyota%20car"
        page.goto(url, timeout=60000)

        page.wait_for_timeout(8000)

        for _ in range(5):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(3000)

        items = page.query_selector_all("a")

        for item in items:
            try:
                text = item.inner_text().lower()
                href = item.get_attribute("href")

                if not text or not href:
                    continue

                if any(k in text for k in KEYWORDS):
                    results.append({
                        "title": text[:120],
                        "price": 0,
                        "location": "NSW",
                        "url": "https://facebook.com" + href if href.startswith("/") else href
                    })

                if len(results) >= 20:
                    break

            except:
                continue

        browser.close()

    return results
