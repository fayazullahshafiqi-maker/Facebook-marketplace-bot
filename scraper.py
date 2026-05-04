from playwright.sync_api import sync_playwright
import re

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

        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.new_page()

        page.set_default_timeout(120000)

        for keyword in KEYWORDS:

            try:

                print(f"Searching: {keyword}")

                url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

                page.goto(url)

                # wait longer for Facebook
                page.wait_for_timeout(15000)

                # scroll multiple times
                for _ in range(5):
                    page.mouse.wheel(0, 8000)
                    page.wait_for_timeout(4000)

                body_text = page.locator("body").inner_text()

                lines = body_text.split("\n")

                for line in lines:

                    text = line.strip()

                    if not text:
                        continue

                    # find price lines
                    if re.search(r"AU\\$\\d+", text):

                        results.append({
                            "title": text[:200],
                            "price": 0,
                            "location": "NSW",
                            "url": url
                        })

                print(f"Collected: {len(results)} listings")

            except Exception as e:

                print(f"Error with {keyword}: {e}")

                continue

        browser.close()

    # remove duplicates
    unique_results = []

    seen = set()

    for item in results:

        if item["title"] not in seen:

            seen.add(item["title"])

            unique_results.append(item)

    return unique_results[:50]
