from playwright.sync_api import sync_playwright
import time
import re

SEARCHES = [
    "toyota rav4",
    "toyota kluger",
    "toyota prado",
    "toyota hilux",
    "isuzu d-max",
    "toyota hiace"
]

def clean(text):
    return text.replace("\n", " ").strip() if text else ""

def extract_price(text):
    match = re.search(r"AU\\$([\\d,]+)", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0

def scrape_marketplace():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 2000},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )

        page = context.new_page()

        for search in SEARCHES:
            try:
                print(f"Searching: {search}")

                url = f"https://www.facebook.com/marketplace/sydney/search?query={search}"
                page.goto(url, timeout=90000)

                # wait for marketplace content
                page.wait_for_timeout(8000)

                # scroll to load real listings
                for _ in range(6):
                    page.mouse.wheel(0, 4000)
                    page.wait_for_timeout(2000)

                # REAL marketplace cards (important fix)
                cards = page.locator("div[role='article']")

                count = cards.count()
                print("Cards found:", count)

                for i in range(min(count, 40)):
                    try:
                        card = cards.nth(i)
                        text = clean(card.inner_text())

                        # filter junk (THIS fixes your log-in spam)
                        if len(text) < 20:
                            continue
                        if "Log in" in text:
                            continue
                        if "Marketplace" in text and "AU$" not in text:
                            continue

                        price = extract_price(text)

                        # skip empty listings
                        if price == 0 and len(text) < 30:
                            continue

                        # try find link
                        link = card.locator("a").first
                        href = link.get_attribute("href") if link.count() > 0 else None

                        if href and "/marketplace/item/" in href:
                            full_url = "https://www.facebook.com" + href
                        else:
                            full_url = "N/A"

                        item = {
                            "location": "NSW",
                            "price": price,
                            "title": text[:200],
                            "url": full_url
                        }

                        if item not in results:
                            results.append(item)

                    except Exception as e:
                        print("Card error:", e)

            except Exception as e:
                print("Search failed:", search, e)

        browser.close()

    print("TOTAL:", len(results))
    return results
