from scraper import scrape_marketplace

def main():
    data = scrape_marketplace("toyota rav4")

    print("\n===== RESULTS =====\n")

    for i, item in enumerate(data, start=1):
        print(i, item["title"])
        print(item["url"])

if __name__ == "__main__":
    main()
