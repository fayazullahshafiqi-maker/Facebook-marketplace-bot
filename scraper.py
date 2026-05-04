from playwright.sync_api import sync_playwright

KEYWORDS = ["rav4", "kluger", "prado", "hilux", "hiace", "dmax", "d-max"]

SEARCH_URLS = [
    "https://www.facebook.com/marketplace/sydney/search/?query=toyota",
    "https://www.facebook.com/marketplace/sydney/search/?query=car",
]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        for url in SEARCH_URLS:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            # scroll more aggressively (Marketplace needs it)
            for _ in range(8):
                page.mouse.wheel(0, 6000)
                page.wait_for_timeout(2500)

            # Marketplace cards (more accurate than <a>)
            cards = page.query_selector_all("div[role='article']")

            for card in cards:
                try:
                    text = card.inner_text().lower()

                    if any(k in text for k in KEYWORDS):
                        link = card.query_selector("a")
                        href = link.get_attribute("href") if link else None

                        results.append({
                            "title": text[:120],
                            "price": 0,
                            "location": "NSW",
                            "url": "https://facebook.com" + href if href and href.startswith("/") else url
                        })

                    if len(results) >= 20:
                        break

                except:
                    continue

        browser.close()

    return results
