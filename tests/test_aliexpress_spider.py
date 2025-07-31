import pytest
from scrapy.http import HtmlResponse, Request
from app.spiders.aliexpress_spider import AliexpressSpider

class TestAliexpressSpider:
    def setup_method(self):
        self.spider = AliexpressSpider()
    
    def test_spider_initialization(self):
        """Test that the AliExpress spider initializes correctly."""
        assert self.spider.name == "aliexpress"
        assert hasattr(self.spider, 'start_requests')
        assert hasattr(self.spider, 'parse')
        assert hasattr(self.spider, '_extract_with_fallbacks')
        assert hasattr(self.spider, '_parse_price')
    
    def test_spider_custom_settings(self):
        """Test that the AliExpress spider has proper custom settings."""
        assert hasattr(self.spider, 'custom_settings')
        custom_settings = self.spider.custom_settings
        
        # Check essential settings
        assert 'USER_AGENT' in custom_settings
        assert 'DOWNLOAD_DELAY' in custom_settings
        assert 'CONCURRENT_REQUESTS' in custom_settings
        assert 'COOKIES_ENABLED' in custom_settings
        assert 'DEFAULT_REQUEST_HEADERS' in custom_settings
        
        # Verify anti-bot measures
        assert custom_settings['DOWNLOAD_DELAY'] >= 3
        assert custom_settings['CONCURRENT_REQUESTS'] == 1
        assert custom_settings['COOKIES_ENABLED'] == True
        assert 'Chrome' in custom_settings['USER_AGENT']
    
    def test_start_requests(self):
        """Test that start_requests generates proper requests."""
        requests = list(self.spider.start_requests())
        
        # Should generate multiple requests for different search strategies
        assert len(requests) > 5  # Multiple URLs for E28 and F10
        
        for request in requests:
            assert 'bmw' in request.url.lower()
            assert 'aliexpress.com' in request.url
            assert 'series' in request.cb_kwargs
            assert request.callback == self.spider.parse
    
    def test_parse_modern_layout(self):
        """Test parsing with modern AliExpress layout."""
        html_content = """
        <div data-testid="product-item">
            <a href="/item/12345.html" data-testid="product-link">
                <img src="https://ae01.alicdn.com/image.jpg" data-testid="product-image" alt="BMW E28 Part">
            </a>
            <span data-testid="product-title">BMW E28 Engine Mount</span>
            <span data-testid="product-price">$29.99</span>
        </div>
        """
        
        request = Request(url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html")
        response = HtmlResponse(
            url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.spider.parse(response, "E28"))
        
        assert len(results) == 1
        item = results[0]
        
        assert item['title_en'] == "BMW E28 Engine Mount"
        assert item['price'] == 29.99
        assert item['series'] == "E28"
        assert item['source'] == "AliExpress"
        assert 'item/12345.html' in item['ebay_url']
        assert 'ae01.alicdn.com' in item['img_url']
    
    def test_parse_fallback_selectors(self):
        """Test parsing with fallback CSS selectors."""
        html_content = """
        <div class="product-item">
            <a href="/item/67890.html">
                <img src="https://example.com/image2.jpg" alt="BMW F10 Part">
            </a>
            <h3 class="product-title"><a>BMW F10 Brake Pad Set</a></h3>
            <div class="price">€45.50</div>
        </div>
        """
        
        response = HtmlResponse(
            url="https://www.aliexpress.com/w/wholesale-bmw-f10-parts.html",
            body=html_content,
            encoding='utf-8'
        )
        
        results = list(self.spider.parse(response, "F10"))
        
        assert len(results) == 1
        item = results[0]
        
        assert item['title_en'] == "BMW F10 Brake Pad Set"
        assert item['price'] == 45.50
        assert item['series'] == "F10"
        assert item['source'] == "AliExpress"
    
    def test_parse_multiple_items(self):
        """Test parsing multiple items in one response."""
        html_content = """
        <div class="search-item-card-wrapper">
            <a href="/item/111.html">
                <img src="https://example.com/img1.jpg">
            </a>
            <div class="product-title"><a>BMW E28 Oil Filter</a></div>
            <div class="price-current">$15.99</div>
        </div>
        <div class="search-item-card-wrapper">
            <a href="/item/222.html">
                <img src="https://example.com/img2.jpg">
            </a>
            <div class="product-title"><a>BMW E28 Air Filter</a></div>
            <div class="price-current">$22.50</div>
        </div>
        """
        
        request = Request(url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html")
        response = HtmlResponse(
            url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.spider.parse(response, "E28"))
        
        assert len(results) == 2
        assert results[0]['title_en'] == "BMW E28 Oil Filter"
        assert results[1]['title_en'] == "BMW E28 Air Filter"
        assert all(item['source'] == "AliExpress" for item in results)
        assert all(item['series'] == "E28" for item in results)
    
    def test_parse_price_method(self):
        """Test the _parse_price method with various price formats."""
        # Test normal prices
        assert self.spider._parse_price("$29.99") == 29.99
        assert self.spider._parse_price("€45.50") == 45.50
        assert self.spider._parse_price("¥120") == 120.0
        
        # Test price ranges
        assert self.spider._parse_price("$19.99 - $29.99") == 19.99
        assert self.spider._parse_price("€25-40") == 25.0
        
        # Test comma separators
        assert self.spider._parse_price("$1,234.56") == 1234.56
        assert self.spider._parse_price("€1.234,56") == 1234.56
        assert self.spider._parse_price("¥1,234") == 1234.0
        
        # Test invalid prices
        assert self.spider._parse_price("FREE") == 0.0
        assert self.spider._parse_price("Call for price") == 0.0
        assert self.spider._parse_price("") == 0.0
        assert self.spider._parse_price(None) == 0.0
    
    def test_extract_with_fallbacks(self):
        """Test the _extract_with_fallbacks method."""
        html_content = """
        <div class="test-item">
            <span class="title">Test Title</span>
            <div class="price">$19.99</div>
            <a href="/test">Link</a>
        </div>
        """
        
        response = HtmlResponse(
            url="https://example.com",
            body=html_content,
            encoding='utf-8'
        )
        
        item = response.css('.test-item')
        
        # Test successful extraction
        result = self.spider._extract_with_fallbacks(item, ['.title::text'])
        assert result == "Test Title"
        
        # Test fallback selectors
        result = self.spider._extract_with_fallbacks(item, [
            '.nonexistent::text',
            '.also-nonexistent::text',
            '.title::text'
        ])
        assert result == "Test Title"
        
        # Test no match
        result = self.spider._extract_with_fallbacks(item, [
            '.nonexistent::text',
            '.also-nonexistent::text'
        ])
        assert result is None
    
    def test_parse_blocked_response(self):
        """Test handling of blocked or captcha responses."""
        request = Request(url="https://www.aliexpress.com/blocked")
        response = HtmlResponse(
            url="https://www.aliexpress.com/blocked",
            body="<html><body>Blocked</body></html>",
            encoding='utf-8',
            request=request
        )
        
        results = list(self.spider.parse(response, "E28"))
        assert len(results) == 0
    
    def test_parse_no_items_found(self):
        """Test handling when no product items are found."""
        html_content = """
        <html>
            <head>
                <title>AliExpress Search Results</title>
            </head>
            <body>
                <div class="search-results">
                    <p>No results found</p>
                </div>
            </body>
        </html>
        """
        
        request = Request(url="https://www.aliexpress.com/w/wholesale-nonexistent-parts.html")
        response = HtmlResponse(
            url="https://www.aliexpress.com/w/wholesale-nonexistent-parts.html",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.spider.parse(response, "E28"))
        # Should generate demo data when no items found
        assert len(results) == 3  # E28 has 3 demo items
    
    def test_parse_missing_essential_data(self):
        """Test handling of items with missing essential data."""
        html_content = """
        <div class="product-item">
            <!-- Missing title -->
            <div class="price">$29.99</div>
            <a href="/item/123.html">
                <img src="https://example.com/image.jpg">
            </a>
        </div>
        <div class="product-item">  
            <div class="product-title"><a>BMW E28 Part</a></div>
            <!-- Missing price -->
            <a href="/item/456.html">
                <img src="https://example.com/image2.jpg">
            </a>
        </div>
        <div class="product-item">
            <div class="product-title"><a>BMW E28 Complete Part</a></div>
            <div class="price">$45.99</div>
            <a href="/item/789.html">
                <img src="https://example.com/image3.jpg">
            </a>
        </div>
        """
        
        request = Request(url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html")
        response = HtmlResponse(
            url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.spider.parse(response, "E28"))
        
        # Only one item should be processed (the complete one)
        assert len(results) == 1
        assert results[0]['title_en'] == "BMW E28 Complete Part"
    
    def test_parse_pagination(self):
        """Test pagination handling."""
        html_content = """
        <div class="product-item">
            <div class="product-title"><a>BMW E28 Part</a></div>
            <div class="price">$29.99</div>
            <a href="/item/123.html">
                <img src="https://example.com/image.jpg">
            </a>
        </div>
        <div class="pagination">
            <a class="pagination-next" href="/page2">Next</a>
        </div>
        """
        
        request = Request(url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html")
        response = HtmlResponse(
            url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.spider.parse(response, "E28"))
        
        # Should have one product item and possibly one pagination request
        product_items = [r for r in results if isinstance(r, dict) and 'title_en' in r]
        assert len(product_items) == 1
        
    def test_url_handling(self):
        """Test proper URL handling for links and images."""
        html_content = """
        <div class="product-item">
            <div class="product-title"><a>BMW E28 Part</a></div>
            <div class="price">$29.99</div>
            <a href="/item/relative-link.html">
                <img src="/images/relative-image.jpg">
            </a>
        </div>
        """
        
        request = Request(url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html")
        response = HtmlResponse(
            url="https://www.aliexpress.com/w/wholesale-bmw-e28-parts.html",
            body=html_content,
            encoding='utf-8',
            request=request
        )
        
        results = list(self.spider.parse(response, "E28"))
        
        assert len(results) == 1
        item = results[0]
        
        # URLs should be converted to absolute
        assert item['ebay_url'].startswith('https://www.aliexpress.com')
        assert item['img_url'].startswith('https://www.aliexpress.com')