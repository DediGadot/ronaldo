import pytest
from scrapy.http import HtmlResponse, Request
from app.spiders.schmiedmann_spider import SchmiedmannE28Spider, SchmiedmannF10Spider, SchmiedmannSpider

class TestSchmiedmannSpider:
    def setup_method(self):
        self.base_spider = SchmiedmannSpider()
        self.e28_spider = SchmiedmannE28Spider()
        self.f10_spider = SchmiedmannF10Spider()
    
    def test_spider_initialization(self):
        """Test that the Schmiedmann spiders initialize correctly."""
        assert self.e28_spider.name == "schmiedmann_e28"
        assert self.e28_spider.series == "E28"
        assert self.f10_spider.name == "schmiedmann_f10"
        assert self.f10_spider.series == "F10"
        
        # Test custom settings
        assert 'PLAYWRIGHT_BROWSER_TYPE' in self.base_spider.custom_settings
        assert self.base_spider.custom_settings['CONCURRENT_REQUESTS'] == 1
        assert self.base_spider.custom_settings['USER_AGENT']
    
    def test_eur_to_usd_conversion_rate(self):
        """Test that EUR to USD conversion rate is set."""
        assert hasattr(self.base_spider, 'EUR_TO_USD_RATE')
        assert self.base_spider.EUR_TO_USD_RATE > 0
        assert isinstance(self.base_spider.EUR_TO_USD_RATE, (int, float))
    
    def test_e28_start_requests(self):
        """Test that E28 spider generates proper start requests."""
        requests = list(self.e28_spider.start_requests())
        
        # Should generate multiple requests for different E28 sections
        assert len(requests) >= 3
        
        for request in requests:
            assert 'schmiedmann.com' in request.url
            assert 'bmw-E28' in request.url or 'bmw-e28' in request.url.lower()
            assert request.callback == self.e28_spider.parse
            assert request.meta.get('playwright') == True
    
    def test_f10_start_requests(self):
        """Test that F10 spider generates proper start requests."""
        requests = list(self.f10_spider.start_requests())
        
        # Should generate multiple requests for different F10 sections
        assert len(requests) >= 2
        
        for request in requests:
            assert 'schmiedmann.com' in request.url
            assert 'bmw-f10' in request.url or 'bmw-F10' in request.url
            assert request.callback == self.f10_spider.parse
            assert request.meta.get('playwright') == True
    
    def test_parse_with_products(self):
        """Test parsing with mock Schmiedmann product data."""
        html_content = """
        <html>
        <body>
            <div class="product-inner">
                <div class="small-product-name">BMW E28 M5 Brake Disc Set</div>
                <div class="product-price">€89.99</div>
                <a href="/product/brake-disc-set">
                    <img src="/images/brake-disc.jpg" alt="Brake Disc">
                </a>
            </div>
            <div class="product-inner">
                <div class="small-product-name">BMW E28 Oil Filter Mann</div>
                <div class="product-price">€24.50</div>
                <a href="/product/oil-filter">
                    <img src="/images/oil-filter.jpg" alt="Oil Filter">
                </a>
            </div>
        </body>
        </html>
        """
        
        request = Request(url="https://www.schmiedmann.com/en/bmw-E28/spare-parts-smc1-catn-ol")
        response = HtmlResponse(
            url="https://www.schmiedmann.com/en/bmw-E28/spare-parts-smc1-catn-ol",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.e28_spider.parse(response))
        
        # Should find 2 products
        assert len(results) == 2
        
        # Test first product
        item1 = results[0]
        assert item1['title_en'] == "BMW E28 M5 Brake Disc Set"
        assert item1['price'] == round(89.99 * self.e28_spider.EUR_TO_USD_RATE, 2)
        assert item1['series'] == "E28"
        assert item1['source'] == "Schmiedmann"
        assert 'schmiedmann.com' in item1['ebay_url']
        assert 'brake-disc.jpg' in item1['img_url']
        
        # Test second product
        item2 = results[1]
        assert item2['title_en'] == "BMW E28 Oil Filter Mann"
        assert item2['price'] == round(24.50 * self.e28_spider.EUR_TO_USD_RATE, 2)
        assert item2['series'] == "E28"
        assert item2['source'] == "Schmiedmann"
    
    def test_parse_with_fallback_selectors(self):
        """Test parsing with different CSS selector structures."""
        html_content = """
        <html>
        <body>
            <div class="product-card">
                <h3 class="product-title">BMW F10 Carbon Spoiler</h3>
                <div class="price-display">€299.99</div>
                <a class="product-link" href="/f10-spoiler">
                    <img class="product-image" src="/images/spoiler.jpg">
                </a>
            </div>
        </body>
        </html>
        """
        
        request = Request(url="https://www.schmiedmann.com/en/bmw-f10/tuning-c9-catn-ol")
        response = HtmlResponse(
            url="https://www.schmiedmann.com/en/bmw-f10/tuning-c9-catn-ol",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.f10_spider.parse(response))
        
        assert len(results) == 1
        item = results[0]
        
        assert item['title_en'] == "BMW F10 Carbon Spoiler"
        assert item['price'] == round(299.99 * self.f10_spider.EUR_TO_USD_RATE, 2)
        assert item['series'] == "F10"
        assert item['source'] == "Schmiedmann"
    
    def test_parse_price_method(self):
        """Test the _parse_price method with various price formats."""
        spider = self.base_spider
        
        # Test normal EUR prices
        assert spider._parse_price("€89.99") == round(89.99 * spider.EUR_TO_USD_RATE, 2)
        assert spider._parse_price("€24.50") == round(24.50 * spider.EUR_TO_USD_RATE, 2)
        assert spider._parse_price("299,99 €") == round(299.99 * spider.EUR_TO_USD_RATE, 2)
        
        # Test price ranges (should take lower value)
        assert spider._parse_price("€19.99 - €29.99") == round(19.99 * spider.EUR_TO_USD_RATE, 2)
        assert spider._parse_price("€25-40") == round(25.0 * spider.EUR_TO_USD_RATE, 2)
        
        # Test European decimal format
        assert spider._parse_price("€1.234,56") == round(1234.56 * spider.EUR_TO_USD_RATE, 2)
        assert spider._parse_price("€12,34") == round(12.34 * spider.EUR_TO_USD_RATE, 2)
        
        # Test invalid prices
        assert spider._parse_price("FREE SHIPPING") == 0.0
        assert spider._parse_price("Call for price") == 0.0
        assert spider._parse_price("") == 0.0
        assert spider._parse_price(None) == 0.0
    
    def test_extract_with_fallbacks(self):
        """Test the _extract_with_fallbacks method."""
        html_content = """
        <div class="test-product">
            <h3 class="product-title">Test BMW Part</h3>
            <div class="price">€45.99</div>
            <a href="/test-part">Link</a>
            <img src="/test-image.jpg" alt="Test">
        </div>
        """
        
        response = HtmlResponse(
            url="https://example.com",
            body=html_content,
            encoding='utf-8'
        )
        
        product = response.css('.test-product')
        spider = self.base_spider
        
        # Test successful extraction
        result = spider._extract_with_fallbacks(product, ['.product-title::text'])
        assert result == "Test BMW Part"
        
        # Test fallback selectors
        result = spider._extract_with_fallbacks(product, [
            '.nonexistent::text',
            '.also-nonexistent::text',
            '.product-title::text'
        ])
        assert result == "Test BMW Part"
        
        # Test no match
        result = spider._extract_with_fallbacks(product, [
            '.nonexistent::text',
            '.also-nonexistent::text'
        ])
        assert result is None
    
    def test_enhance_title(self):
        """Test title enhancement with BMW context."""
        spider = self.e28_spider
        
        # Test title without BMW context
        enhanced = spider._enhance_title("Brake Disc Set Front")
        assert "BMW E28" in enhanced
        
        # Test title with BMW already present
        enhanced = spider._enhance_title("BMW E28 Oil Filter")
        assert enhanced == "BMW E28 Oil Filter"
        
        # Test title with BMW but not series
        enhanced = spider._enhance_title("BMW Brake Pad Set")
        assert enhanced == "BMW Brake Pad Set"  # Should not duplicate BMW
    
    def test_is_valid_item(self):
        """Test item validation logic."""
        spider = self.base_spider
        
        # Valid item
        valid_item = {
            'title_en': 'BMW E28 Part',
            'price': 25.99,
            'source': 'Schmiedmann',
            'series': 'E28'
        }
        assert spider._is_valid_item(valid_item) == True
        
        # Missing required field
        invalid_item = {
            'price': 25.99,
            'source': 'Schmiedmann'
            # Missing title_en
        }
        assert spider._is_valid_item(invalid_item) == False
        
        # Invalid price
        invalid_price_item = {
            'title_en': 'BMW E28 Part',
            'price': 0,
            'source': 'Schmiedmann'
        }
        assert spider._is_valid_item(invalid_price_item) == False
    
    def test_is_blocked_or_error(self):
        """Test blocking detection."""
        spider = self.base_spider
        
        # Normal response
        normal_response = HtmlResponse(
            url="https://www.schmiedmann.com/parts",
            body="<html><body>Normal content</body></html>",
            encoding='utf-8',
            status=200
        )
        assert spider._is_blocked_or_error(normal_response) == False
        
        # Blocked response by status
        blocked_response = HtmlResponse(
            url="https://www.schmiedmann.com/parts",
            body="<html><body>Forbidden</body></html>",
            encoding='utf-8',
            status=403
        )
        assert spider._is_blocked_or_error(blocked_response) == True
        
        # Blocked response by content
        blocked_content_response = HtmlResponse(
            url="https://www.schmiedmann.com/blocked",
            body="<html><body>Access denied</body></html>",
            encoding='utf-8',
            status=200
        )
        assert spider._is_blocked_or_error(blocked_content_response) == True
    
    def test_find_next_page(self):
        """Test pagination detection."""
        html_content = """
        <html>
        <body>
            <div class="pagination">
                <a class="next" href="/page2">Next</a>
            </div>
        </body>
        </html>
        """
        
        response = HtmlResponse(
            url="https://www.schmiedmann.com/parts",
            body=html_content,
            encoding='utf-8'
        )
        
        spider = self.base_spider
        next_page = spider._find_next_page(response)
        assert next_page == "/page2"
        
        # Test no pagination
        html_no_pagination = "<html><body>No pagination</body></html>"
        response_no_pagination = HtmlResponse(
            url="https://www.schmiedmann.com/parts",
            body=html_no_pagination,
            encoding='utf-8'
        )
        
        next_page = spider._find_next_page(response_no_pagination)
        assert next_page is None
    
    def test_generate_demo_items_e28(self):
        """Test demo item generation for E28."""
        demo_items = list(self.e28_spider._generate_demo_items())
        
        assert len(demo_items) == 3  # Should generate 3 demo E28 items
        
        for item in demo_items:
            assert item['series'] == "E28"
            assert item['source'] == "Schmiedmann"
            assert item['price'] > 0
            assert 'BMW E28' in item['title_en']
            assert 'BMW E28' in item['description_en']
            assert 'schmiedmann.com' in item['ebay_url']
            assert item['img_url'].startswith('https://')
    
    def test_generate_demo_items_f10(self):
        """Test demo item generation for F10."""
        demo_items = list(self.f10_spider._generate_demo_items())
        
        assert len(demo_items) == 3  # Should generate 3 demo F10 items
        
        for item in demo_items:
            assert item['series'] == "F10"
            assert item['source'] == "Schmiedmann"
            assert item['price'] > 0
            assert 'BMW F10' in item['title_en']
            assert 'BMW F10' in item['description_en']
            assert 'schmiedmann.com' in item['ebay_url']
            assert item['img_url'].startswith('https://')
    
    def test_parse_no_products_found(self):
        """Test handling when no products are found (should generate demo data)."""
        html_content = """
        <html>
        <head>
            <title>Schmiedmann BMW Parts</title>
        </head>
        <body>
            <div class="content">
                <p>No products found in this category</p>
            </div>
        </body>
        </html>
        """
        
        request = Request(url="https://www.schmiedmann.com/en/bmw-E28/empty-category")
        response = HtmlResponse(
            url="https://www.schmiedmann.com/en/bmw-E28/empty-category",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.e28_spider.parse(response))
        
        # Should generate demo data when no products found
        assert len(results) == 3  # E28 has 3 demo items
        
        # Verify demo data properties
        for item in results:
            assert item['source'] == "Schmiedmann"
            assert item['series'] == "E28"
            assert item['price'] > 0
    
    def test_parse_missing_essential_data(self):
        """Test handling of products with missing essential data."""
        html_content = """
        <html>
        <body>
            <div class="product-inner">
                <!-- Missing title -->
                <div class="product-price">€29.99</div>
                <a href="/product/123">
                    <img src="/image.jpg">
                </a>
            </div>
            <div class="product-inner">  
                <div class="small-product-name">BMW E28 Complete Part</div>
                <!-- Missing price -->
                <a href="/product/456">
                    <img src="/image2.jpg">
                </a>
            </div>
            <div class="product-inner">
                <div class="small-product-name">BMW E28 Valid Part</div>
                <div class="product-price">€45.99</div>
                <a href="/product/789">
                    <img src="/image3.jpg">
                </a>
            </div>
        </body>
        </html>
        """
        
        request = Request(url="https://www.schmiedmann.com/en/bmw-E28/test")
        response = HtmlResponse(
            url="https://www.schmiedmann.com/en/bmw-E28/test",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.e28_spider.parse(response))
        
        # Only one item should be processed (the valid one)
        assert len(results) == 1
        assert results[0]['title_en'] == "BMW E28 Valid Part"
    
    def test_url_handling(self):
        """Test proper URL handling for relative links and images."""
        html_content = """
        <html>
        <body>
            <div class="product-inner">
                <div class="small-product-name">BMW E28 Part</div>
                <div class="product-price">€29.99</div>
                <a href="/product/relative-link">
                    <img src="/images/relative-image.jpg">
                </a>
            </div>
        </body>
        </html>
        """
        
        request = Request(url="https://www.schmiedmann.com/en/bmw-E28/parts")
        response = HtmlResponse(
            url="https://www.schmiedmann.com/en/bmw-E28/parts",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.e28_spider.parse(response))
        
        assert len(results) == 1
        item = results[0]
        
        # URLs should be converted to absolute
        assert item['ebay_url'].startswith('https://www.schmiedmann.com')
        assert item['img_url'].startswith('https://www.schmiedmann.com')
        assert '/product/relative-link' in item['ebay_url']
        assert '/images/relative-image.jpg' in item['img_url']
    
    def test_random_headers_generation(self):
        """Test that random headers are generated properly."""
        headers1 = self.e28_spider._get_random_headers()
        headers2 = self.e28_spider._get_random_headers()
        
        # Both should have required headers
        for headers in [headers1, headers2]:
            assert 'User-Agent' in headers
            assert 'Accept' in headers
            assert 'Accept-Language' in headers
            assert 'Chrome' in headers['User-Agent'] or 'Firefox' in headers['User-Agent']
        
        # User agents might be different (random selection)
        # This test might occasionally fail if same random choice is made, but that's expected
    
    def test_custom_settings_configuration(self):
        """Test that custom settings are properly configured."""
        settings = self.base_spider.custom_settings
        
        # Playwright configuration
        assert 'DOWNLOAD_HANDLERS' in settings
        assert 'PLAYWRIGHT_BROWSER_TYPE' in settings
        assert settings['PLAYWRIGHT_BROWSER_TYPE'] == 'chromium'
        
        # Anti-detection measures
        assert settings['DOWNLOAD_DELAY'] >= 3  # Respectful crawling
        assert settings['CONCURRENT_REQUESTS'] == 1  # Single request at a time
        assert settings['ROBOTSTXT_OBEY'] == False
        
        # Headers configuration
        assert 'DEFAULT_REQUEST_HEADERS' in settings
        headers = settings['DEFAULT_REQUEST_HEADERS']
        assert 'Accept' in headers
        assert 'Sec-Ch-Ua' in headers
        
        # User-Agent is set at top level, not in DEFAULT_REQUEST_HEADERS
        assert 'USER_AGENT' in settings