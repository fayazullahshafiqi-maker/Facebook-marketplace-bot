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

BAD_TEXT = [
    "log in",
    "forgotten account",
    "create new listing",
    "marketplace",
    "filters",
    "search results",
    "notify me"
]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        # 🔥 USE SAVED FACEBOOK LOGIN
        context = browser.new_context(storage_state="state.json")

        page = context.new_page()

        for keyword in KEYWORDS:

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            # scroll
            for _ in range(3):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(2000)

            texts = page.evaluate("""
                () => Array.from(document.querySelectorAll('a'))
                    .map(el => el.innerText)
                    .filter(t => t && t.length > 20)
            """)

            for t in texts:

                clean_text = " ".join(t.split())

                lower = clean_text.lower()

                # remove Facebook junk text
                if any(bad in lower for bad in [
                    "log in",
                    "forgotten account",
                    "create new listing",
                    "marketplace",
                    "filters",
                    "search results",
                    "notify me"
                ]):
                    continue

                # keep only likely vehicle listings
                if (
                    "au$" not in lower and
                    "km" not in lower and
                    "toyota" not in lower and
                    "hilux" not in lower and
                    "prado" not in lower and
                    "rav4" not in lower and
                    "hiace" not in lower and
                    "dmax" not in lower
                ):
                    continue

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
