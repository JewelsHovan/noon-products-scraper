# Noon.com Yoga Products Web Scraper

This project demonstrates web scraping techniques using Python to extract product information from Noon.com, specifically focusing on the yoga section. It's designed to be an educational resource for learning about web scraping, asynchronous programming, and data handling.

## Project Overview

The project consists of two main parts:

1. **`get_product_urls.py`**: This script scrapes Noon.com's yoga section to gather a list of product URLs. It navigates through multiple pages of the website and extracts product names and their corresponding URLs.
2. **`scrape_products.py`**: This script takes the list of product URLs generated by `get_product_urls.py` and asynchronously scrapes detailed information for each product. This includes the product's name, description, SKU, brand, images, price, currency, and seller.

## Features

*   **Web Scraping:** Uses `requests` and `BeautifulSoup` to scrape web pages.
*   **Asynchronous Requests:** Employs `aiohttp` for making asynchronous HTTP requests, significantly improving the efficiency of scraping multiple product pages.
*   **Data Extraction:** Extracts structured data from JSON embedded within `<script>` tags on web pages.
*   **Error Handling:** Includes error handling for JSON decoding and missing data.
*   **Rate Limiting:** Implements a delay mechanism to avoid overloading the website's server and to respect `robots.txt` rules.
*   **Checkpointing:** Saves intermediate results to prevent data loss in case of interruptions.
*   **Duplicate Prevention:** Loads previously scraped data to avoid scraping the same products multiple times.

## Prerequisites

Before running the scripts, ensure you have Python 3 installed along with the following libraries:

*   `requests`
*   `beautifulsoup4`
*   `aiohttp`

You can install these dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Scrape Product URLs

First, run `get_product_urls.py` to generate a list of product URLs from Noon.com's yoga section. This script will scrape multiple pages as specified in the `scrape_all_pages` function and save the results to `data/noon_products.json`.

```bash
python get_product_urls.py
```

### Step 2: Scrape Product Details

Next, run `scrape_products.py` to scrape detailed information for each product URL found in `data/noon_products.json`. This script will save partial results to `data/scraped_products/products_partial.json` after each batch and the final results to `data/scraped_products/products_final.json`.

```bash
python scrape_products.py
```

You can adjust the `delay` and `max_workers` parameters in `scrape_products.py` to control the scraping rate and concurrency.

## Data

*   **`data/noon_products.json`**: Contains a list of product names and URLs extracted by `get_product_urls.py`.
*   **`data/scraped_products/products_partial.json`**: Stores intermediate scraping results.
*   **`data/scraped_products/products_final.json`**: Stores the complete scraped product data, including details like name, description, SKU, brand, images, price, currency, and seller.

## Example Data

Here's an example of the structure of the scraped product data:

```json
{
    "name": "sports yoga bag (unisex)",
    "description": "Online shopping for serenity axis. Trusted Shipping to Dubai, Abu Dhabi and all UAE ✓ Great Prices ✓ Secure Shopping ✓ 100% Contactless ✓ Easy Free Returns ✓ Cash on Delivery. Shop Now",
    "sku": "Z5AC0B61AF0EB891347EAZ",
    "brand": "serenity axis",
    "images": [
      "https://f.nooncdn.com/p/pzsku/Z5AC0B61AF0EB891347EAZ/45/_/1729556895/a68629bd-d46c-49e2-8b53-0e8f9616bb18.jpg?format=jpg&amp;width=240",
      "https://f.nooncdn.com/p/pzsku/Z5AC0B61AF0EB891347EAZ/45/_/1729556905/66ce50fe-469f-4ba1-8863-f01b60f34c56.jpg?format=jpg&amp;width=240",
      "https://f.nooncdn.com/p/pzsku/Z5AC0B61AF0EB891347EAZ/45/_/1729556925/8717a027-d122-49b1-92c1-c0a55e273e99.jpg?format=jpg&amp;width=240",
      "https://f.nooncdn.com/p/pzsku/Z5AC0B61AF0EB891347EAZ/45/_/1729556955/0aefa4b0-fa78-4875-b18f-6cccf5f48d82.jpg?format=jpg&amp;width=240",
      "https://f.nooncdn.com/p/pzsku/Z5AC0B61AF0EB891347EAZ/45/_/1729556965/835e1839-9bdb-4970-b9bf-73e09a7afa36.jpg?format=jpg&amp;width=240",
      "https://f.nooncdn.com/p/pzsku/Z5AC0B61AF0EB891347EAZ/45/_/1729556995/b1b87819-ab66-4e20-bfba-3c194db99a2f.jpg?format=jpg&amp;width=240"
    ],
    "price": "90",
    "currency": "AED",
    "seller": "Serenity Axis",
    "url": "https://www.noon.com/uae-en/sports-yoga-bag-unisex/Z5AC0B61AF0EB891347EAZ/p"
  }
```

## Notes

*   This project is for educational purposes only. Always respect website terms of service and robots.txt when scraping.
*   Web scraping can be fragile due to website structure changes. You may need to update the scraping logic if Noon.com changes its HTML structure.
*   Be mindful of the website's server load and your own bandwidth usage when scraping.

## Contributing

Contributions to this project are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.