import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from urllib.parse import urljoin

# Define constants
BASE_URL = "https://dealsheaven.in"
STORES = [
    "Flipkart", "Amazon", "Paytm", "Foodpanda", "Freecharge",
    "paytmmall", "All Stores"
]
CATEGORIES = [
    "All Categories", "Beauty And Personal Care", "Electronics", "Grocery",
    "Recharge"
]
DEALS = ["Hot Deals Online", "Popular Deals"]
CSV_FILENAME = "scraped_deals.csv"

def scrape_page(url, store_name, category_name, csv_writer):
    """Scrape a single page of deals and write data to CSV."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}. Skipping...")
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    all_items = soup.find_all("div", class_="product-item-detail")

    if not all_items:
        print(f"No products found on {url}.")
        return False

    for item in all_items:
        product = {
            "Store": store_name,
            "Category": category_name,
            "Title": "N/A",
            "Image": "N/A",
            "Price": "N/A",
            "Discount": "N/A",
            "Special Price": "N/A",
            "Link": "N/A",
            "Rating": "N/A",
        }

        discount = item.find("div", class_="discount")
        product["Discount"] = discount.text.strip() if discount else "N/A"

        link = item.find("a", href=True)
        product["Link"] = urljoin(BASE_URL, link["href"]) if link else "N/A"

        # Handle images, including lazy-loaded ones
        image = item.find("img", src=True)
        if image and 'data-src' in image.attrs:
            product["Image"] = urljoin(BASE_URL, image["data-src"])
        elif image and 'src' in image.attrs:
            product["Image"] = urljoin(BASE_URL, image["src"])
        else:
            product["Image"] = "https://via.placeholder.com/150"

        details_inner = item.find("div", class_="deatls-inner")

        title = details_inner.find("h3", title=True) if details_inner else None
        product["Title"] = title["title"].strip() if title else "N/A"

        price = details_inner.find("p", class_="price") if details_inner else None
        product["Price"] = price.text.strip() if price else "N/A"

        special_price = details_inner.find("p", class_="spacail-price") if details_inner else None
        product["Special Price"] = special_price.text.strip() if special_price else "N/A"

        rating = details_inner.find("div", class_="star-point") if details_inner else None
        product["Rating"] = rating.text.strip() if rating else "N/A"

        csv_writer.writerow(product.values())
    return True

def scrape_deals(store_name, category_name, csv_writer):
    """Scrape all pages for a store and category."""
    page = 1
    while True:
        # Handle category-specific URLs
        if category_name == "All Categories":
            url = f"{BASE_URL}/store/{store_name.lower()}?page={page}"
        else:
            formatted_category = category_name.lower().replace(" ", "-")
            url = f"{BASE_URL}/category/{formatted_category}?store={store_name.lower()}&page={page}"

        print(f"Scraping {url} for {store_name} in {category_name}...")
        if not scrape_page(url, store_name, category_name, csv_writer):
            break
        page += 1

def main():
    # Ensure CSV file exists
    file_exists = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Store", "Category", "Title", "Image", "Price", "Discount", "Special Price", "Link", "Rating"])

        # Loop through stores and categories
        for store in STORES:
            for category in CATEGORIES:
                scrape_deals(store, category, writer)

        # Scrape deal tabs (Hot Deals Online & Popular Deals)
        for deal_tab in DEALS:
            deal_url = f"{BASE_URL}/{deal_tab.lower().replace(' ', '-')}"
            print(f"Scraping {deal_tab}...")
            scrape_page(deal_url, "Deals Tab", deal_tab, writer)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"Scraping completed in {time.time() - start_time:.2f} seconds.")

