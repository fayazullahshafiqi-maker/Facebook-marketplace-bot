from playwright.sync_api import sync_playwright
import re
import hashlib
import time

KEYWORDS = [
    "toyota rav4", "rav4",
    "toyota kluger", "kluger",
    "toyota prado", "prado",
    "toyota hilux", "hilux",
    "isuzu d-max", "dmax", "d-max",
    "toyota hiace", "hiace"
]

BLOCK_WORDS = [
    "Log in", "Forgotten account", "Marketplace",
    "Create new listing", "Filters", "Notify Me",
    "Sydney, Australia"
]


def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_noise(text):
    return any(b.lower() in text.lower() for b in BLOCK_WORDS)


def make_id(text):
    return hashlib.md5(text.encode()).hexdigest()


def extract_price(text):
    match = re.search(r"\$[\d,]+", text)
    return match.group(0) if match else "N/A"


def extract_url(text):
    # fallback URL extraction if Facebook hides hrefs
    match = re.search(r"https?://[^\s]+", text)
    return match.group(0) if match else "https://facebook.com"


def scrape_marketplace(headless=False):

    results = []
    seen = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136 Safari/537.36"
        )

        page = context.new_page()
        page.set_default_timeout(60000)

        for keyword in KEYWORDS:

            print(f"\n🔍 Searching: {keyword}")

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(6000)

                # scroll slowly to load listings
                for _ in range(5):
                    page.mouse.wheel(0, 6000)
                    page.wait_for_timeout(2000)

                # REAL marketplace containers
                cards = page.locator('div[role="article"]')

                count = cards.count()
                print(f"📦 Found {count} containers")

                for i in range(count):

                    try:
                        card = cards.nth(i)
                        text = clean_text(card.inner_text(timeout=3000))

                        if len(text) < 20:
                            continue

                        if is_noise(text):
                            continue

                        item_id = make_id(text)

                        if item_id in seen:
                            continue

                        seen.add(item_id)

                        price = extract_price(text)
                        url = extract_url(text)

                        result = {
                            "title": text[:200],
                            "price": price,
                            "location": "NSW",
                            "url": url
                        }

                        print("✔", result)
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

    data = scrape_marketplace(headless=False)

    print("\nFINAL RESULTS:\n")

    for item in data:
        print(item)
