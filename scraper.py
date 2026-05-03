from playwright.sync_api import sync_playwright
import time

KEYWORDS = ["prado", "hilux", "landcruiser"]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        page = context.new_page()

        # NOTE: You MUST already be logged in via cookies/session
        page.goto("https://www.facebook.com/marketplace")

        time.sleep(5)

        for keyword in KEYWORDS:
            search_url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword}"
            page.goto(search_url)
            time.sleep(5)

            # scroll to load listings
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                time.sleep(2)

            cards = page.query_selector_all("div[role='article']")

            for card in cards[:10]:
                try:
                    title = card.inner_text().split("\n")[0]

                    results.append({
                        "title": title,
                        "price": None,
                        "location": "Sydney",
                        "url": page.url
                    })
                except:
                    continue

        browser.close()

    return results
