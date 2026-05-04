from playwright.sync_api import sync_playwright
import re
import hashlib

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
    "Create new listing", "Filters", "Notify",
    "Sydney, Australia"
]


def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_price(text):
    match = re.search(r"\$[\d,]+", text)
    return match.group(0) if match else "N/A"


def make_id(text):
    return hashlib.md5(text.encode()).hexdigest()


def is_noise(text):
    t = text.lower()
    return any(b.lower() in t for b in BLOCK_WORDS)


def scrape_marketplace(headless=True):

    results = []
    seen = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136 Safari/537.36"
            )
        )

        page = context.new_page()
        page.set_default_timeout(60000)

        for keyword in KEYWORDS:

            print(f"\n🔍 Searching: {keyword}")

            url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

                # scroll to load more listings
                for _ in range(6):
                    page.mouse.wheel(0, 8000)
                    page.wait_for_timeout(1500)

                # IMPORTANT: grab ALL links, then filter
                links = page.locator("a")
                count = links.count()

                print(f"🔗 raw links found: {count}")

                for i in range(count):

                    try:
                        link = links.nth(i)

                        text = clean_text(link.inner_text(timeout=2000))
                        href = link.get_attribute("href")

                        if not href or not text:
                            continue

                        # must be marketplace item
                        if "/marketplace/item" not in href:
                            continue

                        if len(text) < 20:
                            continue

                        if is_noise(text):
                            continue

                        full_url = (
                            "https://www.facebook.com" + href
                            if href.startswith("/")
                            else href
                        )

                        item_id = make_id(full_url + text)

                        if item_id in seen:
                            continue

                        seen.add(item_id)

                        result = {
                            "title": text[:200],
                            "price": extract_price(text),
                            "location": "NSW",
                            "url": full_url
                        }

                        print("✔", result)
                        results.append(result)

                        if len(results) >= 50:
                            browser.close()
                            return results

                    except:
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
