from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


def scrape_marketplace(query="toyota rav4"):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    url = f"https://www.facebook.com/marketplace/sydney/search?query={query.replace(' ', '%20')}"
    driver.get(url)

    time.sleep(5)

    results = []

    try:
        cards = driver.find_elements(By.XPATH, "//a[contains(@href, '/marketplace/item/')]")

        for card in cards:
            try:
                href = card.get_attribute("href")

                text = card.text.split("\n")

                title = text[0] if len(text) > 0 else ""
                price = text[1] if len(text) > 1 else ""

                results.append({
                    "title": title,
                    "price": price,
                    "url": href,
                    "location": "NSW"
                })

            except Exception:
                continue

    except Exception as e:
        print("Scrape error:", e)

    driver.quit()
    return results
