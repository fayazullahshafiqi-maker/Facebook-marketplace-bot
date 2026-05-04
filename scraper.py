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

            # scroll to load content
            for _ in range(3):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(2000)

            # 🔥 SAFE: extract ALL visible text at once (no DOM iteration)
            texts = page.evaluate("""
                () => Array.from(document.querySelectorAll('a'))
                    .map(a => a.innerText)
                    .filter(t => t && t.length > 15)
            """)

            for text in texts:
                results.append({
                    "title": text[:120],
                    "price": 0,
                    "location": "NSW",
                    "url": page.url
                })

                if len(results) >= 20:
                    break

        browser.close()

    return results
