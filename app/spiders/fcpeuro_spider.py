import scrapy

class FcpeuroSpider(scrapy.Spider):
    name = "fcpeuro"
    
    def start_requests(self):
        # These URLs need to be updated with the actual FCP Euro search URLs for BMW E28 and F10 parts
        urls = {
            "E28": "https://www.fcpeuro.com/search?q=bmw+e28+parts",  # Placeholder URL
            "F10": "https://www.fcpeuro.com/search?q=bmw+f10+parts",  # Placeholder URL
        }
        for series, url in urls.items():
            yield scrapy.Request(url, self.parse, cb_kwargs={'series': series})

    def parse(self, response, series):
        # These selectors need to be updated with the actual CSS selectors from FCP Euro
        # This is a generic example based on common e-commerce site structures
        for item in response.css(".product-grid-item"):  # Placeholder selector
            title = item.css(".product-title::text").get()  # Placeholder selector
            price = item.css(".price::text").get()  # Placeholder selector
            link = item.css("a::attr(href)").get()  # Placeholder selector
            image_url = item.css("img::attr(src)").get()  # Placeholder selector

            if title and price and link and image_url:
                # Clean up price
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
                    "title_he": f"זוהי תיאור ממלא מקום עבור {title}.",
                    "price": price_float,
                    "ebay_url": link,  # Using ebay_url field for compatibility, but it's actually fcpeuro_url
                    "img_url": image_url,
                    "series": series,
                    "source": "FCP Euro",  # Adding source identifier
                    "description_en": f"This is a placeholder description for {title}.",
                    "description_he": f"זוהי תיאור ממלא מקום עבור {title}.",
                }