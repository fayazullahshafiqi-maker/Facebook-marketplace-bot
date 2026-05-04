from playwright.sync_api import sync_playwright

KEYWORDS = ["rav4", "kluger", "prado", "hilux", "dmax", "hiace"]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for keyword in KEYWORDS:

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword}"
            page.goto(url, timeout=60000)

            page.wait_for_timeout(8000)

            # scroll
            for _ in range(3):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(2000)

            # ✅ USE LOCATOR (FIXES _object ERROR)
            items = page.locator("a")

            count = items.count()

            for i in range(min(count, 30)):
                try:
                    text = items.nth(i).inner_text()

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
