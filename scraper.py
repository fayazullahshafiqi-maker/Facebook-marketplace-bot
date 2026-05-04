```python
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
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        page.set_default_timeout(30000)

        for keyword in KEYWORDS:

            print(f"\nSearching: {keyword}")

            try:

                url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

                page.goto(url)

                page.wait_for_timeout(7000)

                # scroll page slowly
                for _ in range(4):

                    page.mouse.wheel(0, 6000)

                    page.wait_for_timeout(2500)

                # listing links
                cards = page.locator('a[href*="/marketplace/item/"]')

                count = cards.count()

                print(f"Found {count} listings")

                for i in range(count):

                    try:

                        card = cards.nth(i)

                        text = clean_text(card.inner_text())

                        href = card.get_attribute("href")

                        if not href:
                            continue

                        if href in seen:
                            continue

                        if len(text) < 15:
                            continue

                        seen.add(href)

                        if href.startswith("/"):
                            href = "https://www.facebook.com" + href

                        # extract price
                        price = "N/A"

                        match = re.search(r"\$[\d,]+", text)

                        if match:
                            price = match.group(0)

                        result = {
                            "title": text[:200],
                            "price": price,
                            "location": "NSW",
                            "url": href
                        }

                        print(result)

                        results.append(result)

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


if __name__ == "__main__":

    data = scrape_marketplace()

    print("\nFINAL RESULTS:\n")

    for item in data:
        print(item)
```
