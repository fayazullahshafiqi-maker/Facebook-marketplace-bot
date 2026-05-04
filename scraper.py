from playwright.sync_api import sync_playwright

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # TEMP test page (safe for Railway)
        page.goto("https://example.com")

        results.append({
            "title": "Test Listing",
            "price": 1000,
            "location": "Sydney NSW",
            "url": page.url
        })

        browser.close()

    return results
