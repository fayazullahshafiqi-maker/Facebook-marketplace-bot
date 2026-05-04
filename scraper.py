from playwright.sync_api import sync_playwright

KEYWORDS = ["rav4", "kluger", "prado", "hilux", "hiace", "dmax", "d-max"]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        url = "https://www.facebook.com/marketplace/sydney/search/?query=toyota"
        page.goto(url, timeout=60000)
        page.wait_for_timeout(8000)

        for _ in range(5):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(2000)

        cards = page.query_selector_all("div[role='article']")

        for card in cards:
            try:
                text = card.inner_text().lower()

                if any(k in text for k in KEYWORDS):
                    link = card.query_selector("a")
                    href = link.get_attribute("href") if link else ""

                    results.append({
                        "title": text[:120],
                        "location": "NSW",
                        "url": "https://facebook.com" + href if href.startswith("/") else href
                    })

                if len(results) >= 20:
                    break

            except:
                continue

        browser.close()

    return results
