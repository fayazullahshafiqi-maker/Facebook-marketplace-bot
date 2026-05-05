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
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def extract_price(text):
    match = re.search(r"AU\\$([\\d,]+)", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0

def is_valid(text):
    bad_words = [
        "log in", "forgotten account", "marketplace",
        "create new listing", "filters", "notify me",
        "within", "search results"
    ]
    t = text.lower()
    return len(text) > 25 and not any(b in t for b in bad_words)

def scrape_marketplace():
    results = []
    seen_urls = set()

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
                print("Searching:", search)

                url = f"https://www.facebook.com/marketplace/sydney/search?query={search}"
                page.goto(url, timeout=90000, wait_until="domcontentloaded")

                page.wait_for_timeout(8000)

                # scroll more to load real items
                for _ in range(7):
                    page.mouse.wheel(0, 5000)
                    page.wait_for_timeout(2000)

                # BEST FIX: only real marketplace cards
                cards = page.locator("div[role='article']")
                count = cards.count()

                print("Cards:", count)

                for i in range(min(count, 50)):
                    try:
                        card = cards.nth(i)
                        text = clean(card.inner_text())

                        if not is_valid(text):
                            continue

                        price = extract_price(text)

                        link_el = card.locator("a").first
                        href = link_el.get_attribute("href") if link_el.count() > 0 else None

                        if not href:
                            continue

                        if "/marketplace/item/" in href:
                            url_full = "https://www.facebook.com" + href
                        else:
                            continue

                        if url_full in seen_urls:
                            continue

                        seen_urls.add(url_full)

                        results.append({
                            "location": "NSW",
                            "price": price,
                            "title": text[:180],
                            "url": url_full
                        })

                    except Exception as e:
                        print("card error:", e)

            except Exception as e:
                print("search failed:", search, e)

        browser.close()

    print("TOTAL CLEAN RESULTS:", len(results))
    return results
