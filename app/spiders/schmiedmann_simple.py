import scrapy
import re
from urllib.parse import urljoin
from datetime import datetime
from typing import Generator, Dict, Any, Optional

class SchmiedmannSimpleE28Spider(scrapy.Spider):
    """Simple spider for BMW E28 parts without Playwright - uses regular HTTP requests"""
    
    name = "schmiedmann_simple_e28"
    allowed_domains = ['schmiedmann.com']
    
    # Simple settings without Playwright
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 10,
        'AUTOTHROTTLE_MAX_DELAY': 20,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': True,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
        },
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 403],
    }
    
    EUR_TO_USD_RATE = 1.08
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.series = "E28"
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate requests for BMW E28 parts from Schmiedmann."""
        
        urls = [
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-engine-and-driveline-mc12-catn-ol",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-brakes-chassis-suspension-mc13-catn-ol",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-lighting-heater-and-interior-mc14-catn-ol",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-electronic-parts-mc15-catn-ol",
            # Add pagination to get more parts from each category
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-engine-and-driveline-mc12-catn-ol?page=2",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-brakes-chassis-suspension-mc13-catn-ol?page=2",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-lighting-heater-and-interior-mc14-catn-ol?page=2",
            # Add some known working subcategories that might have different parts
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-engine-and-driveline-mc12-catn-ol?itemsPerPage=48",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-brakes-chassis-suspension-mc13-catn-ol?itemsPerPage=48",
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                dont_filter=True,
                headers={
                    'Referer': 'https://www.schmiedmann.com/',
                }
            )
    
    def parse(self, response, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """Parse Schmiedmann parts pages."""
        
        self.logger.info(f"📄 Parsing {response.url} for {self.series} parts (Status: {response.status})")
        
        # Look for products using the confirmed working selector
        products = response.css('.product-inner')
        
        if not products:
            self.logger.warning(f"❌ No products found on {response.url}")
            return
        
        self.logger.info(f"✅ Found {len(products)} products using .product-inner selector")
        
        item_count = 0
        for product in products:
            try:
                item = self._extract_product_data(product, response)
                if item and self._is_valid_item(item):
                    item_count += 1
                    yield item
                    
            except Exception as e:
                self.logger.warning(f"Error processing product: {e}")
                continue
        
        self.logger.info(f"Successfully processed {item_count} items from {response.url}")
        
        # Look for pagination
        next_page = self._find_next_page(response)
        if next_page and item_count > 0:
            next_url = urljoin(response.url, next_page)
            self.logger.info(f"Following pagination to: {next_url}")
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                headers={'Referer': response.url}
            )
    
    def _extract_product_data(self, product, response) -> Optional[Dict[str, Any]]:
        """Extract product data from a product element."""
        
        # Extract title from the specific class we found
        title = product.css('.small-product-name::text').get()
        if title:
            title = title.strip()
        
        # Extract price from the specific structure we found
        price_text = None
        price_span = product.css('.product-price span:first-child::text').get()
        if price_span:
            price_text = price_span.strip() + " EUR"
        
        # Alternative price extraction if first method fails
        if not price_text:
            all_text = product.css('*::text').getall()
            for text in all_text:
                text_clean = text.strip()
                # Look for EUR prices or numeric values followed by EUR
                if ('EUR' in text_clean and any(c.isdigit() for c in text_clean)) or \
                   (text_clean.replace('.', '').replace(',', '').isdigit() and len(text_clean) > 0):
                    price_text = text_clean
                    break
        
        # Extract product link
        link = product.css('a::attr(href)').get()
        
        # Extract image
        image_url = product.css('img::attr(src)').get()
        
        # Extract SKU for additional info
        sku = None
        all_text = ' '.join(product.css('*::text').getall())
        if 'SKU' in all_text:
            import re
            sku_match = re.search(r'SKU\s+([\w-]+)', all_text)
            if sku_match:
                sku = sku_match.group(1)
        
        # Skip if essential data is missing
        if not title or not price_text:
            self.logger.warning(f"Missing data - Title: '{title}', Price: '{price_text}'")
            return None
        
        # Clean and process data
        title = title.strip()
        price_float = self._parse_price(price_text)
        
        # Convert relative URLs to absolute
        if link:
            link = urljoin(response.url, link)
        if image_url:
            image_url = urljoin(response.url, image_url)
        
        # Enhance title with BMW context if needed
        if 'BMW' not in title.upper():
            title = f"BMW {self.series} {title}"
        
        return {
            'title_en': title,
            'title_he': f"{title} - BMW {self.series}",  # Simple Hebrew title
            'price': price_float,
            'img_url': image_url or 'https://via.placeholder.com/300x300/1E90FF/FFFFFF?text=BMW+Part',
            'ebay_url': link or response.url,
            'series': self.series,
            'source': 'Schmiedmann',
            'description_en': f"BMW {self.series} part from Schmiedmann: {title}",
            'description_he': f"חלק BMW {self.series} מ-Schmiedmann: {title}",
            'fetched_at': datetime.now()
        }
    
    def _parse_price(self, price_text: str) -> float:
        """Parse price from text and convert EUR to USD."""
        if not price_text:
            return 0.0
        
        try:
            # Remove all non-digit and non-decimal characters except comma and dot
            price_clean = re.sub(r'[^\d.,]', '', price_text)
            
            if not price_clean:
                return 0.0
            
            # Handle European decimal format (1.234,56 -> 1234.56)
            if ',' in price_clean and '.' in price_clean:
                # Both comma and dot present - comma is thousands separator
                price_clean = price_clean.replace(',', '')
            elif ',' in price_clean:
                # Only comma - could be decimal separator in European format
                parts = price_clean.split(',')
                if len(parts) == 2 and len(parts[1]) == 2:
                    # Likely decimal: 12,34 -> 12.34
                    price_clean = price_clean.replace(',', '.')
                elif len(parts) > 2:
                    # Multiple commas - thousand separators
                    price_clean = price_clean.replace(',', '')
            
            price_eur = float(price_clean)
            # Convert EUR to USD
            return round(price_eur * self.EUR_TO_USD_RATE, 2)
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Could not parse price '{price_text}': {e}")
            return 0.0
    
    def _is_valid_item(self, item: Dict[str, Any]) -> bool:
        """Validate that an item has required data."""
        required_fields = ['title_en', 'price', 'source']
        return all(item.get(field) for field in required_fields) and item['price'] > 0
    
    def _find_next_page(self, response) -> Optional[str]:
        """Find next page URL for pagination."""
        next_selectors = [
            '.pagination .next::attr(href)',
            '.pagination-next::attr(href)',
            'a[rel="next"]::attr(href)',
            '.next-page::attr(href)',
            'a[class*="next"]::attr(href)',
            'a:contains("Next")::attr(href)',
            'a:contains("►")::attr(href)',
            'a:contains("→")::attr(href)',
        ]
        
        for selector in next_selectors:
            next_url = response.css(selector).get()
            if next_url:
                return next_url
        return None


class SchmiedmannSimpleF10Spider(SchmiedmannSimpleE28Spider):
    """Simple spider for BMW F10 parts without Playwright"""
    
    name = "schmiedmann_simple_f10"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.series = "F10"
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate requests for BMW F10 parts from Schmiedmann."""
        
        urls = [
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-engine-and-driveline-mc12-catn-ol",
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-brakes-chassis-suspension-mc13-catn-ol",
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-lighting-heater-and-interior-mc14-catn-ol",
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-electronic-parts-mc15-catn-ol",
            # Add pagination to get more parts from each category
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-engine-and-driveline-mc12-catn-ol?page=2",
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-brakes-chassis-suspension-mc13-catn-ol?page=2", 
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-lighting-heater-and-interior-mc14-catn-ol?page=2",
            # Add different display options to get more variety
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-engine-and-driveline-mc12-catn-ol?itemsPerPage=48",
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-brakes-chassis-suspension-mc13-catn-ol?itemsPerPage=48",
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                dont_filter=True,
                headers={
                    'Referer': 'https://www.schmiedmann.com/',
                }
            )