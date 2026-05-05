from scraper import scrape_marketplace

def main():
    query = "toyota rav4"
    
    print(f"Scraping Facebook Marketplace for: {query} ...")
    
    data = scrape_marketplace(query)

    print("\n===== RESULTS =====\n")

    if not data:
        print("No results found.")
        return

    for i, item in enumerate(data, start=1):
        print(f"{i}. {item.get('title')}")
        print(f"   Price: {item.get('price')}")
        print(f"   URL: {item.get('url')}")
        print(f"   Location: {item.get('location')}")
        print("-" * 50)


if __name__ == "__main__":
    main()
