from playwright.sync_api import sync_playwright

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


def scrape_marketplace():

    results = []

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
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        page.set_default_timeout(120000)

        for keyword in KEYWORDS:

            try:

                print(f"\nSearching: {keyword}")

                url = f"https://www.facebook.com/marketplace/sydney/search?query={keyword.replace(' ', '%20')}"

                page.goto(url, wait_until="domcontentloaded")

                # wait for marketplace to load
                page.wait_for_timeout(15000)

                # scroll to load more listings
                for _ in range(5):

                    page.mouse.wheel(0, 10000)

                    page.wait_for_timeout(3000)

                links = page.locator("a").all()

                print(f"Found {len(links)} links")

                for link in links:

                    try:

                        text = link.inner_text().strip()

                        href = link.get_attribute("href")

                        if not text:
                            continue

                        if not href:
                            continue

                        if "/marketplace/item/" not in href:
                            continue

                        if len(text) < 5:
                            continue

                        if href.startswith("http"):
                            full_url = href
                        else:
                            full_url = f"https://facebook.com{href}"

                        results.append({
                            "title": text[:200],
                            "price": 0,
                            "location": "NSW",
                            "url": full_url
                        })

                    except Exception:
                        continue

                print(f"Current total results: {len(results)}")

            except Exception as e:

                print(f"ERROR with {keyword}: {e}")

                continue

        browser.close()

    # remove duplicate URLs
    unique_results = []

    seen = set()

    for item in results:

        if item["url"] not in seen:

            seen.add(item["url"])

            unique_results.append(item)

    print(f"\nFINAL UNIQUE RESULTS: {len(unique_results)}")

    return unique_results[:50]


if __name__ == "__main__":

    data = scrape_marketplace()

    for item in data:

        print(item)
