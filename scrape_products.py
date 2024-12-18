import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
from headers import headers
from pathlib import Path
import time

class ProductScraper:
    """
    A class to scrape product details from a website asynchronously.
    It uses aiohttp for making requests and BeautifulSoup for parsing HTML.
    """
    def __init__(self, delay=1, max_workers=5):
        """
        Initializes the ProductScraper with a delay and maximum number of worker tasks.

        Args:
            delay (int): The delay in seconds between requests to the same domain.
            max_workers (int): The maximum number of concurrent tasks.
        """
        self.delay = delay
        self.max_workers = max_workers
        self.last_request_time = {}  # Track last request time per domain
        self.session = None
        
    async def init_session(self):
        """
        Initializes an aiohttp ClientSession if it doesn't exist.
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers=headers)

    async def get_product_details(self, url):
        """
        Asynchronously scrapes product details from a given URL.

        Args:
            url (str): The URL of the product page.

        Returns:
            dict: A dictionary containing product details, or None if scraping fails.
        """
        # Implement delay per domain
        domain = url.split('/')[2]
        if domain in self.last_request_time:
            time_since_last = time.time() - self.last_request_time[domain]
            if time_since_last < self.delay:
                await asyncio.sleep(self.delay - time_since_last)
        
        try:
            async with self.session.get(url, timeout=60) as response:
                self.last_request_time[domain] = time.time()
                html = await response.text()
                
            soup = BeautifulSoup(html, 'html.parser')
            
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

    async def close(self):
        """
        Closes the aiohttp ClientSession.
        """
        if self.session:
            await self.session.close()

async def scrape_all_products(delay=1, max_workers=5):
    """
    Asynchronously scrapes product details from a list of product URLs.
    It uses a worker pool to limit the number of concurrent tasks.

    Args:
        delay (int): The delay in seconds between requests to the same domain.
        max_workers (int): The maximum number of concurrent tasks.
    """
    # Load existing products to avoid duplicates
    try:
        with open('data/scraped_products/products_partial.json', 'r', encoding='utf-8') as f:
            existing_products = json.load(f)
            existing_urls = {p['url'] for p in existing_products}
    except FileNotFoundError:
        existing_products = []
        existing_urls = set()

    # Read product URLs
    with open('data/noon_products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)

    # Filter out already scraped products
    new_products = [p for p in products_data if p['url'] not in existing_urls]
    
    Path("data/scraped_products").mkdir(parents=True, exist_ok=True)
    
    scraper = ProductScraper(delay=delay, max_workers=max_workers)
    await scraper.init_session()
    
    async def process_batch(batch):
        """
        Processes a batch of product URLs asynchronously.

        Args:
            batch (list): A list of product URLs.

        Returns:
            list: A list of dictionaries containing product details.
        """
        tasks = []
        for product in batch:
            task = asyncio.create_task(scraper.get_product_details(product['url']))
            tasks.append(task)
        return await asyncio.gather(*tasks)

    # Process in batches based on max_workers
    results = []
    total_new = len(new_products)
    
    for i in range(0, total_new, max_workers):
        batch = new_products[i:i + max_workers]
        print(f"Processing batch {i//max_workers + 1}, products {i+1}-{min(i+max_workers, total_new)}/{total_new}")
        
        batch_results = await process_batch(batch)
        results.extend([r for r in batch_results if r])
        
        # Save checkpoint after each batch
        all_products = existing_products + results
        with open('data/scraped_products/products_partial.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)

    await scraper.close()
    
    # Save final results
    all_products = existing_products + results
    with open('data/scraped_products/products_final.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    print(f"Scraping completed. New products scraped: {len(results)}, Total products: {len(all_products)}")

if __name__ == "__main__":
    # can change delay and max_workers
    asyncio.run(scrape_all_products(delay=0.5, max_workers=10))
