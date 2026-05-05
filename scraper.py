
from playwright.sync_api import sync_playwright
import re
import time

SEARCHES = [
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
    if not text:
        return ""
    return text.replace("\n", " ").strip()

def extract_price(text):
    try:
        match = re.search(r"AU\\$([\\d,]+)", text)
        if match:
            return int(match.group(1).replace(",", ""))
    except:
        pass
    return 0

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 2000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        for search in SEARCHES:
            try:
                url = f"https://www.facebook.com/marketplace/sydney/search?query={search}"

                print(f"Searching: {search}")

                page.goto(url, timeout=90000, wait_until="domcontentloaded")

                time.sleep(8)

                # Scroll multiple times
                for _ in range(5):
                    page.mouse.wheel(0, 5000)
                    time.sleep(2)

                links = page.locator("a[href*='/marketplace/item/']")

                count = links.count()

                print(f"Found {count} cards")

                for i in range(min(count, 50)):
                    try:
                        card = links.nth(i)

                        href = card.get_attribute("href")

                        if not href:
                            continue

                        full_text = clean_text(card.inner_text())

                        if len(full_text) < 5:
                            continue

                        lines = full_text.split()

                        location = "NSW"

                        price = extract_price(full_text)

                        title = full_text[:200]

                        item = {
                            "location": location,
                            "price": price,
                            "title": title,
                            "url": href
                        }

                        # Prevent duplicates
                        already_exists = False

                        for existing in results:
                            if existing["url"] == href:
                                already_exists = True
                                break

                        if not already_exists:
                            results.append(item)

                    except Exception as e:
                        print(f"Card error: {e}")

            except Exception as e:
                print(f"Search failed: {search} | {e}")

        browser.close()

    print(f"TOTAL RESULTS: {len(results)}")

    return results

