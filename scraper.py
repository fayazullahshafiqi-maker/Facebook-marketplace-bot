python
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


def clean_text(text):
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def scrape_marketplace():

    results = []
    seen = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        # better loading
        page.set_default_timeout(60000)

        for keyword in KEYWORDS:

            print(f"Searching: {keyword}")

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            try:

                page.goto(url, wait_until="networkidle")

                page.wait_for_timeout(5000)

                # scroll a bit
                for _ in range(5):
                    page.mouse.wheel(0, 8000)
                    page.wait_for_timeout(2000)

                # get marketplace cards
                cards = page.locator('a[href*="/marketplace/item"]')

                count = cards.count()

                print(f"Found {count} cards")

                for i in range(count):

                    try:

                        card = cards.nth(i)

                        text = clean_text(card.inner_text())

                        href = card.get_attribute("href")

                        if not text:
                            continue

                        if len(text) < 10:
                            continue

                        if href in seen:
                            continue

                        seen.add(href)

                        full_url = href

                        if href.startswith("/"):
                            full_url = "https://facebook.com" + href

                        # extract price
                        price_match = re.search(r"\$[\d,]+", text)

                        price = 0

                        if price_match:
                            price = price_match.group(0)

                        results.append({
                            "title": text[:200],
                            "price": price,
                            "location": "NSW",
                            "url": full_url
                        })

                        print(text[:120])

                        if len(results) >= 50:
                            browser.close()
                            return results

                    except Exception as e:
                        print("Card error:", e)
                        continue

            except Exception as e:
                print("Search error:", e)
                continue

        browser.close()

    return results

