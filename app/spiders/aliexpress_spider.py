import scrapy
import re
import random
from urllib.parse import quote

class AliexpressSpider(scrapy.Spider):
    name = "aliexpress"
    
    # Add custom settings for better scraping with improved anti-bot measures
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 8,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'COOKIES_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
        'RETRY_TIMES': 2,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 403],
        'HTTPERROR_ALLOWED_CODES': [403, 404],
    }
    
    def start_requests(self):
        """Generate initial requests for Ronaldo items"""
        
        # Ronaldo items search terms by category and era
        search_terms = {
            ("jerseys", "United"): ["cristiano ronaldo manchester united jersey", "ronaldo united shirt"],
            ("jerseys", "Madrid"): ["cristiano ronaldo real madrid jersey", "ronaldo madrid shirt"], 
            ("jerseys", "Juventus"): ["cristiano ronaldo juventus jersey", "ronaldo juventus shirt"],
            ("jerseys", "Portugal"): ["cristiano ronaldo portugal jersey", "ronaldo portugal shirt"],
            ("jerseys", "Al-Nassr"): ["cristiano ronaldo al nassr jersey", "ronaldo al nassr shirt"],
            ("memorabilia", "General"): ["cristiano ronaldo memorabilia", "ronaldo collectible"],
            ("boots", "General"): ["cristiano ronaldo boots", "ronaldo football shoes"],
            ("cards", "General"): ["cristiano ronaldo card", "ronaldo trading card"],
        }
        
        for (category, era), terms in search_terms.items():
            for search_term in terms:
                url = f"https://www.aliexpress.com/wholesale?SearchText={quote(search_term)}"
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    cb_kwargs={'category': category, 'era': era},
                    headers=self._get_random_headers(),
                    dont_filter=True,
                    meta={'category': category, 'era': era, 'search_term': search_term}
                )
    
    def _get_random_headers(self):
        """Generate randomized headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def parse(self, response, category, era):
        """Parse AliExpress search results with fallback to demo data"""
        
        # Check for blocking indicators
        blocking_indicators = ["blocked", "captcha", "punish", "verification", "forbidden"]
        page_content = response.text.lower()
        is_blocked = any(indicator in page_content for indicator in blocking_indicators)
        
        if is_blocked or response.status == 403:
            self.logger.warning(f"🚫 Blocked/CAPTCHA detected for {response.url}. Using demo data.")
            yield from self._generate_demo_data(category, era)
            return

        # Try to parse real data
        items_found = False
        
        # Multiple selectors to try
        selectors = [
            "div.list--gallery--34TrPt1 div.list-item",
            "div.search-item-card-wrapper",
            "div[data-spm-anchor-id]",
            "div.item"
        ]
        
        for selector in selectors:
            items = response.css(selector)
            if items:
                self.logger.info(f"✅ Found {len(items)} items using selector: {selector}")
                items_found = True
                break
        
        if not items_found:
            self.logger.warning(f"⚠️ No items found with any selector. Using demo data for {category}/{era}")
            yield from self._generate_demo_data(category, era)
            return
            
        # Parse found items
        for item in items[:10]:  # Limit to avoid overwhelming
            title = self._extract_text(item, [
                "h1::text", "h2::text", "h3::text", ".item-title::text",
                "a[title]::attr(title)", ".title::text"
            ])
            
            price = self._extract_text(item, [
                ".price-current::text", ".price::text", 
                "[class*='price']::text", ".notranslate::text"
            ])
            
            link = self._extract_link(item, [
                "a::attr(href)", "a[href*='item']::attr(href)"
            ])
            
            image_url = self._extract_text(item, [
                "img::attr(src)", "img::attr(data-src)", 
                "img::attr(data-lazy-src)"
            ])

            if title and price and link:
                # Clean and process data
                price_float = self._extract_price(price)
                full_link = response.urljoin(link) if link else ""
                
                # Extract additional info
                team = self._extract_team(title, era)
                year = self._extract_year(title)
                size = self._extract_size(title)
                condition = self._extract_condition(title)

                yield {
                    "title_en": title,
                    "price": price_float,
                    "item_url": full_link,
                    "img_url": image_url,
                    "era": era,
                    "category": category,
                    "team": team,
                    "year": year,
                    "size": size,
                    "condition": condition,
                    "source": "AliExpress",
                    "description_en": f"Cristiano Ronaldo {category.replace('_', ' ')} from {era} era. {title}",
                    "description_he": f"פריט של כריסטיאנו רונאלדו מתקופת {era}. {title}",
                }

    def _extract_text(self, item, selectors):
        """Try multiple selectors to extract text"""
        for selector in selectors:
            result = item.css(selector).get()
            if result:
                return result.strip()
        return ""

    def _extract_link(self, item, selectors):
        """Try multiple selectors to extract link"""
        for selector in selectors:
            result = item.css(selector).get()
            if result and 'item' in result:
                return result.strip()
        return ""

    def _extract_price(self, price_text):
        """Extract numeric price from price text"""
        if not price_text:
            return 0.0
        
        # Remove currency symbols and extract number
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        price_clean = re.sub(r'[,.](?=\d{3})', '', price_clean)  # Remove thousands separators
        
        try:
            return float(price_clean)
        except ValueError:
            return 0.0

    def _extract_team(self, title, era):
        """Extract team name from title based on era"""
        teams = {
            "Sporting": "Sporting CP",
            "United": "Manchester United", 
            "Madrid": "Real Madrid",
            "Juventus": "Juventus",
            "Portugal": "Portugal National Team",
            "Al-Nassr": "Al-Nassr"
        }
        return teams.get(era, era)

    def _extract_year(self, title):
        """Extract year from title"""
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        return year_match.group() if year_match else None

    def _extract_size(self, title):
        """Extract clothing size from title"""
        size_match = re.search(r'\b(XS|S|M|L|XL|XXL|\d+)\b', title.upper())
        return size_match.group() if size_match else None

    def _extract_condition(self, title):
        """Extract condition from title"""
        if re.search(r'\b(new|brand new)\b', title.lower()):
            return "New"
        elif re.search(r'\b(used|pre-owned)\b', title.lower()):
            return "Used"
        elif re.search(r'\b(replica|fake)\b', title.lower()):
            return "Replica"
        return "New"

    def _generate_demo_data(self, category, era):
        """Generate demo Ronaldo items when real scraping fails"""
        demo_items = {
            ("jerseys", "United"): [
                {
                    "title_en": "Cristiano Ronaldo Manchester United Home Jersey 2021-22",
                    "price": 89.99,
                    "team": "Manchester United",
                    "year": "2021",
                    "size": "L",
                    "condition": "New"
                },
                {
                    "title_en": "Ronaldo #7 Manchester United Away Jersey",
                    "price": 75.50,
                    "team": "Manchester United", 
                    "year": "2022",
                    "size": "M",
                    "condition": "New"
                }
            ],
            ("jerseys", "Madrid"): [
                {
                    "title_en": "Cristiano Ronaldo Real Madrid Home Jersey 2016-17",
                    "price": 99.99,
                    "team": "Real Madrid",
                    "year": "2017",
                    "size": "L",
                    "condition": "New"
                },
                {
                    "title_en": "Ronaldo #7 Real Madrid Champions League Jersey",
                    "price": 120.00,
                    "team": "Real Madrid",
                    "year": "2018",
                    "size": "XL", 
                    "condition": "New"
                }
            ],
            ("memorabilia", "General"): [
                {
                    "title_en": "Cristiano Ronaldo Signed Photo with COA",
                    "price": 299.99,
                    "team": "General",
                    "year": "2023",
                    "size": "8x10",
                    "condition": "New"
                }
            ]
        }

        items = demo_items.get((category, era), [])
        
        for i, item_data in enumerate(items):
            yield {
                "title_en": item_data["title_en"],
                "price": item_data["price"],
                "item_url": f"https://www.aliexpress.com/item/demo-{category}-{era}-{i}.html",
                "img_url": f"https://via.placeholder.com/400x400/ff0000/ffffff?text=Ronaldo+{category.title()}",
                "era": era,
                "category": category,
                "team": item_data["team"],
                "year": item_data["year"],
                "size": item_data["size"],
                "condition": item_data["condition"],
                "authenticity": "Unverified",
                "source": "AliExpress",
                "description_en": f"Demo: {item_data['title_en']} - This is demonstration data.",
                "description_he": f"דמו: {item_data['title_en']} - זהו מידע הדגמה.",
            }