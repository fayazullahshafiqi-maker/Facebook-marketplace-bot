from scraper import scrape_marketplace

def main():
    query = "toyota rav4"
    data = scrape_marketplace(query)

    print("\n🔥 FLIPSENTRY RESULTS 🔥\n")

    for i, item in enumerate(data, 1):
        print(f"{i}. {item['title']}")
        print(item['url'])
        print("-" * 40)

if __name__ == "__main__":
    main()
