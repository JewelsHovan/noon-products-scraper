import requests
from bs4 import BeautifulSoup
import json
from headers import headers

def get_product_details(url):
    """
    Scrape product details from a noon.com product page
    """
    
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
                'seller': None
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
        print(f"Error scraping product: {e}")
        return None

# Test the function with a single URL
if __name__ == "__main__":
    test_url = "https://www.noon.com/uae-en/cork-yoga-mat-blue-lotus/Z9D8DAAC82282938FD1BFZ/p"
    product = get_product_details(test_url)
    
    if product:
        print("Product details:")
        print(json.dumps(product, indent=2))
    else:
        print("Failed to get product details")
