from playwright.sync_api import sync_playwright
import time

KEYWORDS = ["prado", "hilux", "hiace", "dmax"]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        page = context.new_page()

        for keyword in KEYWORDS:
            print(f"🔍 Searching: {keyword}")

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword}"
            page.goto(url)
            time.sleep(5)

            # scroll to load listings
            for _ in range(3):
                page.mouse.wheel(0, 2500)
                time.sleep(2)

            cards = page.query_selector_all("div[role='article']")

            for card in cards[:10]:
                try:
                    text = card.inner_text().split("\n")

                    title = text[0] if text else "Unknown"

                    link_el = card.query_selector("a")
                    link = "https://facebook.com" + link_el.get_attribute("href") if link_el else page.url

                    results.append({
                        "title": title,
                        "price": None,
                        "location": "Sydney",
                        "url": link,
                        "source": "facebook"
                    })

                except:
                    continue

        browser.close()

    return results
