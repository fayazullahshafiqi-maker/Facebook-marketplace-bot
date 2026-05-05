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


def clean(text):
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def is_noise(text):
    bad = [
        "log in", "forgotten account", "marketplace",
        "create new listing", "filters", "notify me",
        "within", "sort by", "sydney, australia"
    ]
    t = text.lower()
    return any(x in t for x in bad)


def looks_like_listing(text):
    # real listing usually has price OR km OR model year
    return (
        "$" in text or
        "km" in text.lower() or
        "20" in text  # year hint
    )


def scrape():

    results = []
    seen = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()
        page.set_default_timeout(60000)

        for kw in KEYWORDS:

            print(f"\n🔎 Searching: {kw}")

            url = f"https://www.facebook.com/marketplace/sydney/search?query={kw.replace(' ', '%20')}"

            try:
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(6)

                # 🔥 detect fake page (login shell)
                body_text = page.inner_text("body").lower()

                if "log in" in body_text and "marketplace" in body_text:
                    print("⚠ Login shell detected (not real feed)")

                # wait for real listings
                try:
                    page.wait_for_selector('a[href*="/marketplace/item"]', timeout=15000)
                except:
                    print("❌ No listings loaded")
                    continue

                # slow scroll (important for FB lazy load)
                for _ in range(6):
                    page.mouse.wheel(0, 9000)
                    time.sleep(2)

                links = page.locator('a[href*="/marketplace/item"]')
                count = links.count()

                print(f"📦 Raw elements: {count}")

                for i in range(count):

                    try:
                        el = links.nth(i)

                        text = clean(el.inner_text())
                        href = el.get_attribute("href")

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
                        m = re.search(r"\$[\d,]+", text)
                        if m:
                            price = m.group(0)

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

    data = scrape()

    print("\nFINAL RESULTS:\n")

    for d in data:
        print(d)
