import scrapy


class SparetoSpider(scrapy.Spider):
    name = "spareto"
    
    def start_requests(self):
        # URLs for Spareto BMW parts search
        # Note: Spareto seems to have limited BMW E28/F10 specific parts
        # We'll search for general BMW parts that may be compatible
        urls = {
            "E28": "https://www.spareto.com/products?keywords=BMW+E28",
            "F10": "https://www.spareto.com/products?keywords=BMW+F10",
        }
        for series, url in urls.items():
            yield scrapy.Request(url, self.parse, cb_kwargs={'series': series})
    
    def parse(self, response, series):
        # Check if there are results for this search
        no_results = response.css(".no-results::text").get()
        if no_results and "Nothing Matches your Search" in no_results:
            self.logger.info(f"No results found for BMW {series} parts on Spareto")
            return
        
        # Extract parts from the search results
        # Based on our analysis, Spareto uses classes like:
        # .card-product for individual items
        # .card-product .name for titles
        # .card-product-price for prices
        # .card-product-image img for images
        # .card-product a for links
        
        for item in response.css(".card-product"):
            title = item.css(".name::text").get()
            price_element = item.css(".card-product-price")
            price = price_element.css("::text").get() if price_element else None
            link = item.css("a::attr(href)").get()
            image_url = item.css(".card-product-image img::attr(src)").get()
            
            # If we can't get complete information, skip this item
            if not all([title, price, link, image_url]):
                continue
            
            # Clean up price (remove currency symbols, commas, etc.)
            price_str = price.replace("$", "").replace(",", "").strip()
            try:
                price_float = float(price_str)
            except ValueError:
                price_float = 0.0
            
            # Ensure absolute URLs
            if link.startswith("/"):
                link = response.urljoin(link)
            if image_url.startswith("/"):
                image_url = response.urljoin(image_url)
            
            yield {
                "title_en": title.strip(),
                "price": price_float,
                "ebay_url": link,  # Using ebay_url field for compatibility
                "img_url": image_url,
                "series": series,
                "source": "Spareto",  # Adding source identifier
                "description_en": f"This is a placeholder description for {title}.",
                "description_he": f"זוהי תיאור ממלא מקום עבור {title}.",
            }