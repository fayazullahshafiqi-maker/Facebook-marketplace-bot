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

            # scroll to load more listings
            for _ in range(3):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(2000)

            # SAFE extraction (no Playwright DOM objects)
            texts = page.evaluate("""
                () => Array.from(document.querySelectorAll('a'))
                    .map(el => el.innerText)
                    .filter(t => {
                        if (!t) return false;
                        const text = t.toLowerCase();

                        return (
                            t.length > 40 &&
                            (
                                text.includes('au$') ||
                                text.includes('km') ||
                                text.includes('toyota') ||
                                text.includes('prado') ||
                                text.includes('rav4') ||
                                text.includes('hilux') ||
                                text.includes('hiace') ||
                                text.includes('dmax')
                            )
                        );
                    })
            """)

            for t in texts:
                clean_text = " ".join(t.split())

                results.append({
                    "title": clean_text[:150],
                    "price": 0,
                    "location": "NSW",
                    "url": page.url
                })

                if len(results) >= 25:
                    break

        browser.close()

    return results
