from playwright.sync_api import sync_playwright
import re

KEYWORDS = [
    "toyota rav4",
    "toyota kluger",
    "toyota prado",
    "toyota hilux",
    "isuzu d-max",
    "toyota hiace"
]

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        for keyword in KEYWORDS:

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            page.goto(url, timeout=60000)
            page.wait_for_timeout(10000)

            for _ in range(3):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(2000)

            listings = page.locator('a[href*="/marketplace/item"]').all()

            for listing in listings:
                try:
                    text = listing.inner_text()

                    if not text:
                        continue

                    if "AU$" not in text:
                        continue

                    lines = text.split("\n")

                    title = ""
                    price = 0
                    location = "NSW"

                    for line in lines:
                        if "AU$" in line:
                            price_match = re.findall(r'\d[\d,]*', line)

                            if price_match:
                                price = int(price_match[0].replace(",", ""))

                    if len(lines) >= 2:
                        title = lines[1]

                    href = listing.get_attribute("href")

                    if href:
                        if href.startswith("/"):
                            href = "https://facebook.com" + href

                    results.append({
                        "title": title,
                        "price": price,
                        "location": location,
                        "url": href
                    })

                except:
                    continue

        browser.close()

    return results
