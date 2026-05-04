from playwright.sync_api import sync_playwright
import re
import time

KEYWORDS = [
    "toyota rav4", "rav4",
    "toyota kluger", "kluger",
    "toyota prado", "prado",
    "toyota hilux", "hilux",
    "isuzu d-max", "dmax", "d-max",
    "toyota hiace", "hiace"
]


def clean_text(text):
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def is_bad_text(text):
    bad_words = [
        "log in", "forgotten account", "marketplace",
        "create new listing", "filters", "notify me",
        "sydney, australia", "within", "sort by"
    ]
    t = text.lower()
    return any(b in t for b in bad_words)


def scrape_marketplace():

    results = []
    seen = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        page.set_default_timeout(60000)

        for keyword in KEYWORDS:

            print(f"\n🔎 Searching: {keyword}")

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            try:
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(5)

                # wait until real listings appear
                try:
                    page.wait_for_selector('a[href*="/marketplace/item"]', timeout=10000)
                except:
                    print("⚠ No listings detected, retrying...")
                    continue

                # scroll properly (wait for content change)
                last_height = 0

                for _ in range(5):
                    page.mouse.wheel(0, 8000)
                    time.sleep(2)

                # grab ALL links
                links = page.locator('a[href*="/marketplace/item"]')
                count = links.count()

                print(f"📦 Found {count} raw elements")

                for i in range(count):

                    try:
                        el = links.nth(i)

                        text = clean_text(el.inner_text())
                        href = el.get_attribute("href")

                        if not href:
                            continue

                        if is_bad_text(text):
                            continue

                        if len(text) < 15:
                            continue

                        if href in seen:
                            continue

                        seen.add(href)

                        if href.startswith("/"):
                            href = "https://www.facebook.com" + href

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

    print("\nFINAL RESULTS:\n")

    for d in data:
        print(d)
