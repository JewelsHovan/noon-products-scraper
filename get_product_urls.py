import requests
from bs4 import BeautifulSoup
from typing import List
import json
import time
from headers import headers

#url = 'https://www.noon.com/_next/data/bigalog-a18cbfcc8fcee7b143949c818af903078f57319d/uae-en/sports-and-outdoors/exercise-and-fitness/yoga-16328.json?isCarouselView=false&limit=50&page=2&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc&catalog=sports-and-outdoors&catalog=exercise-and-fitness&catalog=yoga-16328'

url = f'https://www.noon.com/uae-en/sports-and-outdoors/exercise-and-fitness/yoga-16328/?isCarouselView=false&limit=50&page=2'

def extract_product_info(json_data):
    """Extracts product names and URLs from a JSON string."""
    try:
        data = json_data
        products = []
        for item in data.get("itemListElement", []):
            url = item.get("url", "N/A")
            # Clean the URL by removing everything after '/p' but keeping the '/p'
            clean_url = url.split('/p/')[0] + '/p' if '/p/' in url else url
            
            # Extract the product name from URL
            parts = clean_url.split('/')
            product_name_part = parts[-2]
            # Replace - with space and remove any additional characters from URL part
            product_name = product_name_part.replace("-", " ").strip()
            
            products.append({
                "name": product_name,
                "url": clean_url
            })
        return products
    except (AttributeError, TypeError) as e:
        print(f"Error processing JSON data: {e}")
        return None
    
def find_and_extract_json(html_content):
    """
    Finds and extracts the specific JSON data from within a <script> tag 
    that contains product information, identified by the @type "ItemList".
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script', type='application/ld+json')
    
    if not script_tags:
        return None

    for script_tag in script_tags:
        try:
            json_data = json.loads(script_tag.string)
            # Check if the parsed JSON is of @type "ItemList"
            if json_data.get('@type') == 'ItemList' and "itemListElement" in json_data:
                return json_data
        except json.JSONDecodeError:
            # Continue to the next script if parsing fails
            continue
    return None

def scrape_page(page_number):
    """Scrape a single page and return the products"""
    url = f'https://www.noon.com/uae-en/sports-and-outdoors/exercise-and-fitness/yoga-16328/?isCarouselView=false&limit=50&page={page_number}'
    
    response = requests.get(url, headers=headers, timeout=60)
    json_data = find_and_extract_json(response.text)
    
    if json_data:
        return extract_product_info(json_data)
    return []

def scrape_all_pages(start_page=1, end_page=5):
    """Scrape multiple pages and combine the results"""
    all_products = []
    
    for page in range(start_page, end_page + 1):
        print(f"Scraping page {page}...")
        products = scrape_page(page)
        if products:
            all_products.extend(products)
            print(f"Found {len(products)} products on page {page}")
        else:
            print(f"No products found on page {page}")
        # Add a small delay between requests to be polite
        time.sleep(2)
    
    return all_products

# Main execution
if __name__ == "__main__":
    # Scrape pages 1 through 5
    all_products = scrape_all_pages(1, 5)
    
    if all_products:
        print(f"\nTotal products found: {len(all_products)}")
        # Save to JSON file
        with open('noon_products.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print("Products saved to noon_products.json")
    else:
        print("No products were found")