import scrapy
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

class RockAutoSpider(scrapy.Spider):
    name = 'rockauto'
    allowed_domains = ['rockauto.com']
    
    def __init__(self, *args, **kwargs):
        super(RockAutoSpider, self).__init__(*args, **kwargs)
        
        # URLs for BMW E28 and F10 parts
        self.start_urls = [
            'https://www.rockauto.com/en/mbmw,840313,e28/1987,parts/,5-series.html',
            'https://www.rockauto.com/en/mbmw,1132906,f10-f11-f07/2010,parts/,5-series.html'
        ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }
    
    def parse(self, response):
        """Parse the main BMW E28 or F10 parts page"""
        # Determine which BMW series we're scraping
        series = 'f10' if 'f10-f11-f07' in response.url.lower() else 'e28'
        
        # RockAuto uses a complex structure with tables - find all part listings
        parts_tables = response.css('table.listing') or response.css('table[cellspacing="1"]')
        
        for table in parts_tables:
            parts_rows = table.css('tbody tr')
            
            for row in parts_rows:
                try:
                    # Extract part information
                    part_number = row.css('.listing-number::text').get()
                    title = row.css('.listing-text-description::text, .listing-text-strong::text').get()
                    price = row.css('.listing-price-num::text, .price::text').get()
                    img_url = row.css('.listing-img img::attr(src)').get()
                    product_url = row.css('a.listing-text-description::attr(href)').get()
                    
                    if not title or not price:
                        continue
                    
                    # Clean up the data
                    title = title.strip() if title else ""
                    price = self.clean_price(price)
                    
                    # Resolve relative URLs
                    if product_url:
                        product_url = urljoin(response.url, product_url)
                    
                    if img_url:
                        img_url = urljoin(response.url, img_url)
                        # RockAuto typically uses small thumbnails - try to get larger versions
                        img_url = self.get_larger_image(img_url)
                    
                    if price > 0:  # Only include parts with valid prices
                        yield {
                            'title_en': title,
                            'title_he': '',  # Will be translated later
                            'price': price,
                            'img_url': img_url or '',
                            'product_url': product_url or '',
                            'source': 'RockAuto',
                            'series': series.upper(),
                            'description_en': f"BMW {series.upper()} part from RockAuto",
                            'description_he': '',
                            'part_number': part_number.strip() if part_number else '',
                            'fetched_at': datetime.utcnow().isoformat()
                        }
                
                except Exception as e:
                    self.logger.warning(f"Error parsing part row: {e}")
                    continue
        
        # Optional: Follow pagination if exists
        next_page = response.css('a.pagination-link.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
    
    def clean_price(self, price_text):
        """Clean and convert price to float"""
        if not price_text:
            return 0.0
        
        # Remove currency symbols and commas, extract number
        price_str = re.sub(r'[\$,\s]+', '', price_text.strip())
        
        try:
            return float(price_str)
        except ValueError:
            # Handle cases like "From $19.79" or "Call for Price"
            match = re.search(r'\d+\.\d+', price_str)
            if match:
                return float(match.group())
            return 0.0
    
    def get_larger_image(self, img_url):
        """Try to get a larger image URL from RockAuto"""
        if not img_url:
            return img_url
        
        # RockAuto typically uses URLs with dimensions like "_s.jpg"
        # Replace with larger size
        img_url = re.sub(r'_s\.(jpg|jpeg|png|gif)', r'_l.\1', img_url, flags=re.IGNORECASE)
        img_url = re.sub(r'_m\.(jpg|jpeg|png|gif)', r'_l.\1', img_url, flags=re.IGNORECASE)
        
        return img_url