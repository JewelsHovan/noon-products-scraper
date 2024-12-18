import requests
from bs4 import BeautifulSoup
import json
from headers import headers
import time
from pathlib import Path

def get_product_details(url):
    """
    Scrape product details from a noon.com product page
    """
    # Add delay to avoid overwhelming the server
    time.sleep(1)
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all script tags with type application/ld+json
        script_tags = soup.find_all('script', type='application/ld+json')
        
        # Find the script tag containing product information
        product_data = None
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'Product':
                    product_data = data
                    break
            except json.JSONDecodeError:
                continue
        
        if product_data:
            # Extract relevant information
            product = {
                'name': product_data.get('name'),
                'description': product_data.get('description'),
                'sku': product_data.get('sku'),
                'brand': product_data.get('brand', {}).get('name'),
                'images': product_data.get('image', []),
                'price': None,
                'currency': None,
                'seller': None,
                'url': url  # Add the URL to the product data
            }
            # Extract price information from offers
            if offers := product_data.get('offers', []):
                if isinstance(offers, list) and offers:
                    first_offer = offers[0]
                    product['price'] = first_offer.get('price')
                    product['currency'] = first_offer.get('priceCurrency')
                    product['seller'] = first_offer.get('seller', {}).get('name')
            
            return product
            
        return None
        
    except Exception as e:
        print(f"Error scraping product {url}: {e}")
        return None

def scrape_all_products():
    """
    Scrape all products from noon_products.json and save results
    """
    # Read product URLs from JSON file
    try:
        with open('data/noon_products.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)
    except Exception as e:
        print(f"Error reading products file: {e}")
        return

    # Create output directory if it doesn't exist
    Path("data/scraped_products").mkdir(parents=True, exist_ok=True)
    
    # Initialize results list
    scraped_products = []
    total_products = len(products_data)
    
    # Scrape each product
    for index, product in enumerate(products_data, 1):
        url = product.get('url')
        if not url:
            continue
            
        print(f"Scraping product {index}/{total_products}: {url}")
        
        product_details = get_product_details(url)
        if product_details:
            scraped_products.append(product_details)
            
        # Save progress every 10 products
        if index % 10 == 0:
            with open('data/scraped_products/products_partial.json', 'w', encoding='utf-8') as f:
                json.dump(scraped_products, f, indent=2, ensure_ascii=False)
    
    # Save final results
    with open('data/scraped_products/products_final.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_products, f, indent=2, ensure_ascii=False)
    
    print(f"Scraping completed. Total products scraped: {len(scraped_products)}")

if __name__ == "__main__":
    scrape_all_products()
