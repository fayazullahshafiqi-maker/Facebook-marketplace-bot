from playwright.sync_api import sync_playwright
import re
import time

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


def clean(text):
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def is_noise(text):

    bad_words = [
        "log in",
        "forgotten account",
        "marketplace",
        "search results",
        "filters",
        "notify me",
        "create new listing",
        "within",
        "sort by",
        "sydney, australia"
    ]

    lower = text.lower()

    for word in bad_words:
        if word in lower:
            return True

    return False


def looks_like_listing(text):

    lower = text.lower()

    if "$" in text:
        return True

    if "km" in lower:
        return True

    years = [
        "200",
        "201",
        "202"
    ]

    for y in years:
        if y in text:
            return True

    return False


def scrape_marketplace():

    results = []
    seen = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context(
            viewport={
                "width": 1280,
                "height": 900
            },
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        page.set_default_timeout(60000)

        for keyword in KEYWORDS:

            print(f"\nSearching: {keyword}")

            try:

                url = (
                    "https://www.facebook.com/marketplace/"
                    f"sydney/search?query={keyword.replace(' ', '%20')}"
                )

                page.goto(
                    url,
                    wait_until="domcontentloaded"
                )

                time.sleep(8)

                body = page.inner_text("body").lower()

                if "log in" in body and "marketplace" in body:
                    print("Facebook login wall detected")

                for _ in range(6):

                    page.mouse.wheel(0, 9000)

                    time.sleep(2)

                cards = page.locator(
    'a[href*="/marketplace/item/"]:visible'
)

                count = cards.count()

                print(f"Found {count} raw cards")

                for i in range(count):

                    try:

                        card = cards.nth(i)

                        text = clean(card.locator("..").inner_text())

                        href = card.get_attribute("href")

if href and "marketplace/item" not in href:
    continue

                        if not href:
                            continue

                        if is_noise(text):
                            continue

                        if not looks_like_listing(text):
                            continue

                        if len(text) < 15:
                            continue

                        if href in seen:
                            continue

                        seen.add(href)

                        if href.startswith("/"):
                            href = "https://www.facebook.com" + href

                        price = "N/A"

                        match = re.search(
                            r"\$[\d,]+",
                            text
                        )

                        if match:
                            price = match.group(0)

                        item = {
                            "title": text[:200],
                            "price": price,
                            "location": "NSW",
                            "url": href
                        }

                        results.append(item)

                        print(item)

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
