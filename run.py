import streamlit as st
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

# Constants for the DealsHeaven website
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

# Default images for each store in case the product doesn't have one
STORE_IMAGES = {
    "flipkart": "https://via.placeholder.com/150?text=Flipkart", 
    "amazon": "https://via.placeholder.com/150?text=Amazon", 
    "paytm": "https://via.placeholder.com/150?text=Paytm", 
    "foodpanda": "https://via.placeholder.com/150?text=Foodpanda",
    "freecharge": "https://via.placeholder.com/150?text=Freecharge",
    "paytmmall": "https://via.placeholder.com/150?text=PaytmMall",
    "all stores": "https://via.placeholder.com/150?text=All+Stores"
}

# Scraping functions
def scrape_page(url, store_name, category_name):
    """Scrape a single page of deals."""
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    all_items = soup.find_all("div", class_="product-item-detail")

    results = []
    for item in all_items:
        product = {
            "Store": store_name,
            "Category": category_name,
            "Title": "N/A",
            "Image": STORE_IMAGES.get(store_name.lower(), STORE_IMAGES["all stores"]),  # Default image
            "Price": "N/A",
            "Discount": "N/A",
            "Special Price": "N/A",
            "Link": "N/A",
            "Rating": "N/A",
        }

        # Attempt to extract discount, link, and image
        discount = item.find("div", class_="discount")
        product["Discount"] = discount.text.strip() if discount else "N/A"

        link = item.find("a", href=True)
        product["Link"] = urljoin(BASE_URL, link["href"]) if link else "N/A"

        image = item.find("img", src=True)
        if image and 'data-src' in image.attrs:
            product["Image"] = urljoin(BASE_URL, image["data-src"])
        elif image and 'src' in image.attrs:
            product["Image"] = urljoin(BASE_URL, image["src"])

        details_inner = item.find("div", class_="deatls-inner")

        title = details_inner.find("h3", title=True) if details_inner else None
        product["Title"] = title["title"].strip() if title else "N/A"

        price = details_inner.find("p", class_="price") if details_inner else None
        product["Price"] = price.text.strip() if price else "N/A"

        special_price = details_inner.find("p", class_="spacail-price") if details_inner else None
        product["Special Price"] = special_price.text.strip() if special_price else "N/A"

        rating = details_inner.find("div", class_="star-point") if details_inner else None
        product["Rating"] = rating.text.strip() if rating else "N/A"

        results.append(product)
    return results

def scrape_deals(store_name, category_name, deal_type, start_page, end_page):
    """Scrape multiple pages of deals."""
    results = []
    for page in range(start_page, end_page + 1):
        # Correct URL construction based on store and category
        if category_name == "All Categories":
            if store_name == "All Stores":
                url = f"{BASE_URL}/?page={page}"  # All stores, all categories
            else:
                url = f"{BASE_URL}/store/{store_name.lower()}?page={page}"  # Specific store, all categories
        else:
            formatted_category = category_name.lower().replace(" ", "-")
            if store_name == "All Stores":
                url = f"{BASE_URL}/category/{formatted_category}?page={page}"  # All stores, specific category
            else:
                url = f"{BASE_URL}/category/{formatted_category}?store={store_name.lower()}&page={page}"  # Specific store, specific category

        st.info(f"Scraping page {page} for {store_name} in {category_name}...")
        page_results = scrape_page(url, store_name, category_name)
        if not page_results:
            break
        results.extend(page_results)
    return results

# Streamlit UI
def main():
    st.set_page_config(
        page_title="DealsHeaven",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Ayushmaan's Product Scraper")
    st.markdown(
        """
        **Welcome!** This tool allows you to scrape and view exciting product deals from [DealsHeaven](https://dealsheaven.in).
        Let's get started!
        """
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
            .stButton>button {
                background-color: #ff4b5c;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                padding: 12px 25px;
            }
            .stButton>button:hover {
                background-color: #f52c3d;
            }
            .product-card {
                border: 1px solid #ddd;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 20px;
                padding: 15px;
                text-align: center;
                transition: transform 0.3s ease;
            }
            .product-card:hover {
                transform: scale(1.05);
            }
            .product-card img {
                border-radius: 8px;
                max-width: 100%;
                height: auto;
            }
            .product-title {
                font-size: 18px;
                font-weight: bold;
                color: white;  /* Changed text color to white */
                background-color: rgba(0, 0, 0, 0.6); /* Added dark background for contrast */
                padding: 10px;
                border-radius: 8px;
            }
            .product-price {
                font-size: 16px;
                color: #f52c3d;
                font-weight: bold;
            }
            .product-link {
                text-decoration: none;
                color: #007bff;
                font-size: 16px;
                font-weight: bold;
            }
            .product-link:hover {
                color: #0056b3;
            }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar for user input
    with st.sidebar:
        st.header("Search Filters")
        store_name = st.selectbox("Select Store", STORES)
        category_name = st.selectbox("Select Category", CATEGORIES)
        deal_type = st.selectbox("Select Deal Type", ["None"] + DEALS, index=0)
        start_page = st.number_input("Start Page", min_value=1, value=1)
        end_page = st.number_input("End Page", min_value=1, value=1)
        scrape_button = st.button("🔍 Start Scraping")

    # Display results if button is clicked
    if scrape_button:
        with st.spinner("Scraping in progress... This might take a few moments..."):
            deal_type = None if deal_type == "None" else deal_type
            results = scrape_deals(store_name, category_name, deal_type, start_page, end_page)

            if results:
                st.success(f"🎉 Found {len(results)} products!")
                search_query = st.text_input("🔎 Search Products", "")
                if search_query:
                    results = [prod for prod in results if search_query.lower() in prod["Title"].lower()]
                    st.info(f"Filtered to {len(results)} results.")

                # Display results as cards
                cols = st.columns(4)
                for idx, product in enumerate(results):
                    with cols[idx % 4]:
                        st.markdown(
                            f"""
                            <div class="product-card">
                                <img src="{product['Image']}" alt="Product Image">
                                <div class="product-title">{product['Title']}</div>
                                <p class="product-price">{product['Price']}</p>
                                <p class="product-price"><b>Special Price:</b> {product['Special Price']}</p>
                                <p class="product-price"><b>Discount:</b> {product['Discount']}</p>
                                <p class="product-price"><b>Rating:</b> {product['Rating']}</p>
                                <a href="{product['Link']}" target="_blank" class="product-link">View Deal</a>
                            </div>
                            """, unsafe_allow_html=True
                        )
            else:
                st.warning("No products found.")

if __name__ == "__main__":
    main()
