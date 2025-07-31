import scrapy
import re
import random
from urllib.parse import urljoin, quote
from datetime import datetime
from typing import Generator, Dict, Any, Optional

class SchmiedmannSpider(scrapy.Spider):
    """Base spider class for Schmiedmann.com BMW parts scraping."""
    
    name = "schmiedmann_base"
    allowed_domains = ['schmiedmann.com']
    
    # Custom settings for JavaScript-heavy content
    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': ['--no-sandbox', '--disable-dev-shm-usage']
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 30000,
        'PLAYWRIGHT_CONTEXTS': {
            'default': {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        },
        'DOWNLOAD_DELAY': 8,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 8,
        'AUTOTHROTTLE_MAX_DELAY': 15,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': True,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        },
        'RETRY_TIMES': 2,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 403],
        'HTTPERROR_ALLOWED_CODES': [403, 404],
    }
    
    # EUR to USD conversion rate (should be updated regularly)
    EUR_TO_USD_RATE = 1.08
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.series = getattr(self, 'series', 'E28')  # Default to E28
        
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate initial requests for BMW parts. To be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement start_requests method")
    
    def parse(self, response, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """Parse Schmiedmann parts pages with multiple fallback strategies."""
        
        # Check for blocking or error pages
        if self._is_blocked_or_error(response):
            self.logger.error(f"🚫 Blocked or error detected for {response.url}")
            return
            
        # Log response details
        self.logger.info(f"📄 Parsing {response.url} for {self.series} parts")
        
        # Try multiple selectors for product containers - comprehensive list
        product_selectors = [
            '.product-inner',
            '.product-card',
            '.product-item', 
            '.item-card',
            '[data-product-id]',
            '.spare-part-item',
            '.product-box',
            '.article-item',
            '.part-card',
            '.catalog-item',
            '.grid-item',
            '.product-tile',
            '.shop-item',
            'article.product',
            'div[class*="product"]',
            'div[class*="item"]',
            'li.product',
            '.product-list-item',
            '.catalog-product',
            '.shop-product',
        ]
        
        products = []
        for selector in product_selectors:
            products = response.css(selector)
            if products:
                self.logger.info(f"✅ Found {len(products)} products using selector: {selector}")
                break
        
        if not products:
            self.logger.warning(f"❌ No products found on {response.url}")
            return
        
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
        
        # Handle pagination
        next_page = self._find_next_page(response)
        if next_page and item_count > 0:
            next_url = urljoin(response.url, next_page)
            self.logger.info(f"Following pagination to: {next_url}")
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={'playwright': True},
                headers={'Referer': response.url}
            )
    
    def _extract_product_data(self, product, response) -> Optional[Dict[str, Any]]:
        """Extract product data from a product element."""
        
        # Extract title with comprehensive fallback selectors
        title = self._extract_with_fallbacks(product, [
            '.small-product-name::text',
            'h3.product-title::text',
            '.product-name::text',
            '.item-title::text',
            '.article-name::text',
            '.part-name::text',
            '.catalog-title::text',
            '.shop-title::text',
            'h1::text',
            'h2::text',
            'h3::text',
            'h4::text',
            '.title::text',
            'a[title]::attr(title)',
            '.product-title::text',
            '.item-name::text',
            '.article-title::text',
            'span.title::text',
            'div.title::text',
            '.name::text',
            '.headline::text',
            'strong::text',
            '.product-heading::text',
        ])
        
        # Extract price with comprehensive fallback selectors
        price_text = self._extract_with_fallbacks(product, [
            '.product-price::text',
            '.price-display::text',
            '.price::text',
            '.cost::text',
            '.amount::text',
            '[data-price]::attr(data-price)',
            '.price-value::text',
            '.item-price::text',
            '.article-price::text',
            '.part-price::text',
            '.shop-price::text',
            '.catalog-price::text',
            'span.price::text',
            'div.price::text',
            '.current-price::text',
            '.sale-price::text',
            '.regular-price::text',
            '.final-price::text',
            '.unit-price::text',
            'strong.price::text',
            '.amount-value::text',
            '.currency::text',
            '.euro::text',
            '.eur::text',
        ])
        
        # Extract product link with comprehensive selectors
        link = self._extract_with_fallbacks(product, [
            'a::attr(href)',
            '.product-link::attr(href)',
            '.item-link::attr(href)',
            '.article-link::attr(href)',
            '.part-link::attr(href)',
            '.catalog-link::attr(href)',
            '.shop-link::attr(href)',
            'a.product::attr(href)',
            'a.item::attr(href)',
            '[data-href]::attr(data-href)',
            '[data-url]::attr(data-url)',
        ])
        
        # Extract image with comprehensive selectors
        image_url = self._extract_with_fallbacks(product, [
            '.product-image img::attr(src)',
            '.item-img img::attr(src)',
            '.article-img img::attr(src)',
            '.part-img img::attr(src)',
            '.catalog-img img::attr(src)',
            '.shop-img img::attr(src)',
            'img::attr(src)',
            'img::attr(data-src)',
            'img::attr(data-lazy)',
            'img::attr(data-original)',
            'img::attr(data-srcset)',
            '.image img::attr(src)',
            '.thumb img::attr(src)',
            '.thumbnail img::attr(src)',
            'picture img::attr(src)',
            '.photo img::attr(src)',
        ])
        
        # Skip if essential data is missing
        if not all([title, price_text]):
            return None
        
        # Clean and process data
        title = title.strip()
        price_float = self._parse_price(price_text)
        
        if price_float <= 0:
            return None
        
        # Ensure absolute URLs
        link = urljoin(response.url, link) if link and not link.startswith("http") else link
        image_url = urljoin(response.url, image_url) if image_url and not image_url.startswith("http") else image_url
        
        # Use placeholder if no image
        if not image_url:
            image_url = "https://via.placeholder.com/300x300/CCCCCC/666666?text=Schmiedmann+Part"
        
        return {
            "title_en": self._enhance_title(title),
            "price": price_float,
            "ebay_url": link or response.url,  # Use page URL as fallback
            "img_url": image_url,
            "series": self.series,
            "source": "Schmiedmann",
            "description_en": f"BMW {self.series} part from Schmiedmann: {title}",
            "description_he": f"חלק BMW {self.series} מ-Schmiedmann: {title}",
        }
    
    def _extract_with_fallbacks(self, selector, fallback_selectors) -> Optional[str]:
        """Try multiple CSS selectors until one returns a value."""
        for css_selector in fallback_selectors:
            try:
                result = selector.css(css_selector).get()
                if result and result.strip():
                    return result.strip()
            except Exception:
                continue
        return None
    
    def _parse_price(self, price_text: str) -> float:
        """Parse price from text, handling EUR currency and conversion."""
        if not price_text:
            return 0.0
        
        # Remove currency symbols and extra whitespace
        price_clean = re.sub(r'[^\d.,\-]', '', price_text).strip()
        
        if not price_clean:
            return 0.0
        
        try:
            # Handle price ranges by taking the lower value
            if '-' in price_clean:
                price_clean = price_clean.split('-')[0].strip()
            
            # Handle European decimal format (1.234,56)
            if ',' in price_clean and '.' in price_clean:
                # Check which appears last - that's likely the decimal separator
                comma_pos = price_clean.rfind(',')
                dot_pos = price_clean.rfind('.')
                if dot_pos > comma_pos:
                    # Format: 1,234.56 - comma is thousand separator
                    price_clean = price_clean.replace(',', '')
                else:
                    # Format: 1.234,56 - comma is decimal separator
                    price_clean = price_clean.replace('.', '').replace(',', '.')
            elif price_clean.count(',') == 1:
                # Check if comma is decimal separator
                comma_pos = price_clean.index(',')
                if len(price_clean) - comma_pos <= 3:
                    # Format: 12,34 - comma is decimal separator
                    price_clean = price_clean.replace(',', '.')
                else:
                    # Format: 1,234 - comma is thousand separator
                    price_clean = price_clean.replace(',', '')
            elif ',' in price_clean:
                # Multiple commas - likely thousand separators
                price_clean = price_clean.replace(',', '')
            
            price_eur = float(price_clean)
            # Convert EUR to USD
            return round(price_eur * self.EUR_TO_USD_RATE, 2)
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Could not parse price '{price_text}': {e}")
            return 0.0
    
    def _enhance_title(self, title: str) -> str:
        """Enhance product title with BMW context."""
        title = title.strip()
        if not any(keyword in title.upper() for keyword in ['BMW', self.series]):
            title = f"BMW {self.series} {title}"
        return title
    
    def _is_valid_item(self, item: Dict[str, Any]) -> bool:
        """Validate that an item has required data."""
        required_fields = ['title_en', 'price', 'source']
        return all(item.get(field) for field in required_fields) and item['price'] > 0
    
    def _is_blocked_or_error(self, response) -> bool:
        """Check if response indicates blocking or errors."""
        blocking_indicators = [
            "blocked", "captcha", "access denied", "forbidden",
            "too many requests", "rate limit", "error"
        ]
        
        page_content = response.text.lower()
        current_url = response.url.lower()
        
        return (
            response.status >= 400 or
            any(indicator in current_url or indicator in page_content 
                for indicator in blocking_indicators)
        )
    
    def _find_next_page(self, response) -> Optional[str]:
        """Find next page URL for pagination with comprehensive selectors."""
        next_selectors = [
            '.pagination .next::attr(href)',
            '.pagination-next::attr(href)',
            'a[rel="next"]::attr(href)',
            '.next-page::attr(href)',
            '.pager-next::attr(href)',
            '.paginator .next::attr(href)',
            '.page-next::attr(href)',
            'a.next::attr(href)',
            'a.forward::attr(href)',
            '.arrow-right::attr(href)',
            '.next-link::attr(href)',
            'a[title*="next"]::attr(href)',
            'a[title*="Next"]::attr(href)',
            'a[class*="next"]::attr(href)',
            'a[class*="forward"]::attr(href)',
            '.pages .next::attr(href)',
            '.paging .next::attr(href)',
            '.page-nav .next::attr(href)',
            'a:contains("Next")::attr(href)',
            'a:contains("►")::attr(href)',
            'a:contains("→")::attr(href)',
            'a:contains(">")::attr(href)',
            '.pagination li:last-child a::attr(href)',
        ]
        
        for selector in next_selectors:
            next_url = response.css(selector).get()
            if next_url:
                return next_url
        return None
    
    def _generate_demo_items(self) -> Generator[Dict[str, Any], None, None]:
        """Generate demo data when no products are found."""
        demo_parts = {
            "E28": [
                {
                    "title_en": f"BMW E28 OE Brake Disc Set Front - Schmiedmann",
                    "price": 89.99 * self.EUR_TO_USD_RATE,
                    "img_url": "https://via.placeholder.com/300x300/1E90FF/FFFFFF?text=BMW+E28+Brake+Disc",
                    "ebay_url": "https://www.schmiedmann.com/en/bmw-E28/demo-brake-disc.html",
                    "description_en": "Original Equipment brake disc set for BMW E28 front axle. High quality replacement part from Schmiedmann.",
                    "description_he": "סט דיסקי בלמים מקוריים עבור BMW E28 ציר קדמי. חלק חלופי באיכות גבוהה מ-Schmiedmann."
                },
                {
                    "title_en": f"BMW E28 Engine Oil Filter - Mann Filter",
                    "price": 24.50 * self.EUR_TO_USD_RATE,
                    "img_url": "https://via.placeholder.com/300x300/32CD32/FFFFFF?text=BMW+E28+Oil+Filter",
                    "ebay_url": "https://www.schmiedmann.com/en/bmw-E28/demo-oil-filter.html",
                    "description_en": "Mann-Filter oil filter for BMW E28 engines. Premium quality filtration for optimal engine protection.",
                    "description_he": "מסנן שמן Mann-Filter עבור מנועי BMW E28. סינון באיכות פרמיום להגנה אופטימלית על המנוע."
                },
                {
                    "title_en": f"BMW E28 Interior Door Handle Set - Left/Right",
                    "price": 65.75 * self.EUR_TO_USD_RATE,
                    "img_url": "https://via.placeholder.com/300x300/FF6347/FFFFFF?text=BMW+E28+Door+Handle",
                    "ebay_url": "https://www.schmiedmann.com/en/bmw-E28/demo-door-handle.html",
                    "description_en": "Complete interior door handle set for BMW E28. Includes left and right side handles with mounting hardware.",
                    "description_he": "סט ידיות דלת פנימיות שלם עבור BMW E28. כולל ידיות צד שמאל וימין עם חומרת הרכבה."
                }
            ],
            "F10": [
                {
                    "title_en": f"BMW F10 M Performance Carbon Fiber Spoiler",
                    "price": 299.99 * self.EUR_TO_USD_RATE,
                    "img_url": "https://via.placeholder.com/300x300/800080/FFFFFF?text=BMW+F10+Spoiler",
                    "ebay_url": "https://www.schmiedmann.com/en/bmw-f10/demo-carbon-spoiler.html",
                    "description_en": "M Performance carbon fiber rear spoiler for BMW F10 5-Series. Genuine BMW accessory for enhanced aerodynamics.",
                    "description_he": "ספויילר אחורי מסיבי פחמן M Performance עבור BMW F10 5-Series. אביזר BMW מקורי לשיפור האווירודינמיקה."
                },
                {
                    "title_en": f"BMW F10 LED Angel Eyes Headlight Set",
                    "price": 450.00 * self.EUR_TO_USD_RATE,
                    "img_url": "https://via.placeholder.com/300x300/FFD700/000000?text=BMW+F10+LED+Lights",
                    "ebay_url": "https://www.schmiedmann.com/en/bmw-f10/demo-led-headlights.html",
                    "description_en": "LED Angel Eyes headlight set for BMW F10. Modern LED technology with adaptive lighting functionality.",
                    "description_he": "סט פנסי ראש LED Angel Eyes עבור BMW F10. טכנולוגיית LED מודרנית עם פונקציונליות תאורה אדפטיבית."
                },
                {
                    "title_en": f"BMW F10 Adaptive Suspension Strut - Front",
                    "price": 189.95 * self.EUR_TO_USD_RATE,
                    "img_url": "https://via.placeholder.com/300x300/4169E1/FFFFFF?text=BMW+F10+Suspension",
                    "ebay_url": "https://www.schmiedmann.com/en/bmw-f10/demo-suspension-strut.html",
                    "description_en": "Adaptive suspension strut for BMW F10 front axle. Electronic damping control for superior ride comfort.",
                    "description_he": "תומך מתלה אדפטיבי עבור BMW F10 ציר קדמי. בקרת בולם אלקטרונית לנוחות נסיעה מעולה."
                }
            ]
        }
        
        parts_list = demo_parts.get(self.series, demo_parts["E28"])
        
        for part in parts_list:
            yield {
                "title_en": part["title_en"],
                "price": round(part["price"], 2),
                "ebay_url": part["ebay_url"],
                "img_url": part["img_url"],
                "series": self.series,
                "source": "Schmiedmann",
                "description_en": part["description_en"],
                "description_he": part["description_he"],
            }


class SchmiedmannE28Spider(SchmiedmannSpider):
    """Spider specifically for BMW E28 parts on Schmiedmann.com"""
    
    name = "schmiedmann_e28"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.series = "E28"
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate requests for BMW E28 parts from Schmiedmann."""
        
        # Real E28 subcategory URLs that contain actual products
        urls = [
            # Engine and driveline parts (confirmed working)
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-engine-and-driveline-mc12-catn-ol",
            
            # Brakes, chassis, suspension (confirmed working) 
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-brakes-chassis-suspension-mc13-catn-ol",
            
            # Lighting, heater and interior
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-lighting-heater-and-interior-mc14-catn-ol",
            
            # Electronic parts
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-electronic-parts-mc15-catn-ol",
            
            # Additional URLs with display options to get more products per page
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-engine-and-driveline-mc12-catn-ol?itemsPerPage=96",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-brakes-chassis-suspension-mc13-catn-ol?itemsPerPage=96",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-lighting-heater-and-interior-mc14-catn-ol?itemsPerPage=96",
            "https://www.schmiedmann.com/en/bmw-E28/spare-parts-electronic-parts-mc15-catn-ol?itemsPerPage=96",
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'playwright': True},
                headers=self._get_random_headers(),
                dont_filter=True
            )
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate randomized headers."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-US,en;q=0.5']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }


class SchmiedmannF10Spider(SchmiedmannSpider):
    """Spider specifically for BMW F10 parts on Schmiedmann.com"""
    
    name = "schmiedmann_f10"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.series = "F10"
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate requests for BMW F10 parts from Schmiedmann."""
        
        # Real F10 subcategory URLs that contain actual products
        urls = [
            # Engine and driveline parts (confirmed working)
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-engine-and-driveline-mc12-catn-ol",
            
            # Brakes, chassis, suspension
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-brakes-chassis-suspension-mc13-catn-ol",
            
            # Lighting, heater and interior
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-lighting-heater-and-interior-mc14-catn-ol",
            
            # Electronic parts
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-electronic-parts-mc15-catn-ol",
            
            # Additional URLs with display options to get more products per page
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-engine-and-driveline-mc12-catn-ol?itemsPerPage=96",
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-brakes-chassis-suspension-mc13-catn-ol?itemsPerPage=96", 
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-lighting-heater-and-interior-mc14-catn-ol?itemsPerPage=96",
            "https://www.schmiedmann.com/en/bmw-f10/spare-parts-electronic-parts-mc15-catn-ol?itemsPerPage=96",
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'playwright': True},
                headers=self._get_random_headers(),
                dont_filter=True
            )
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate randomized headers."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-US,en;q=0.5']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }