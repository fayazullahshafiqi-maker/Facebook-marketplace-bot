from playwright.sync_api import sync_playwright
import re
import time

KEYWORDS = [
    "toyota rav4",
    "toyota kluger",
    "toyota prado",
    "toyota hilux",
    "isuzu d-max",
    "toyota hiace"
]


def clean_text(text):
    if not text:
        return ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_valid_listing(text, href):
    if not href:
        return False

    bad_texts = [
        "Log in",
        "Forgotten account",
        "Marketplace",
        "Create new listing",
        "Filters",
        "Notify Me",
        "Search results"
    ]

    if any(bad in text for bad in bad_texts):
        return False

    # must look like a marketplace item
    if "/marketplace/item/" not in href:
        return False

    if len(text) < 15:
        return False

    return True


def scrape_marketplace():
    results = []
    seen = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=50
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )

        page = context.new_page()
        page.set_default_timeout(60000)

        for keyword in KEYWORDS:

            print(f"\n🔎 Searching: {keyword}")

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(8000)

                # scroll more properly (important fix)
                last_height = 0

                for _ in range(8):

                    page.mouse.wheel(0, 8000)
                    page.wait_for_timeout(2000)

                    # stop early if page stops loading
                    current_height = page.evaluate("document.body.scrollHeight")
                    if current_height == last_height:
                        break
                    last_height = current_height

                # IMPORTANT FIX: broader selector
                cards = page.locator('a[href*="/marketplace/"]')

                count = cards.count()
                print(f"Found raw elements: {count}")

                for i in range(count):

                    try:
                        card = cards.nth(i)

                        text = clean_text(card.inner_text())
                        href = card.get_attribute("href")

                        if not href:
                            continue

                        if href.startswith("/"):
                            href = "https://www.facebook.com" + href

                        if not is_valid_listing(text, href):
                            continue

                        if href in seen:
                            continue

                        seen.add(href)

                        price_match = re.search(r"\$[\d,]+", text)
                        price = price_match.group(0) if price_match else "N/A"

                        item = {
                            "title": text[:200],
                            "price": price,
                            "location": "NSW",
                            "url": href
                        }

                        results.append(item)
                        print("✔", item)

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

    print("\n\nFINAL RESULTS:\n")

    for d in data:
        print(d)
