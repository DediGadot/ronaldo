import scrapy
import re

class EbaySpider(scrapy.Spider):
    name = "ebay"
    
    def start_requests(self):
        # Ronaldo items by era and category
        searches = {
            ("Sporting", "jerseys"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+sporting+lisbon+jersey&_sacat=0",
            ("United", "jerseys"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+manchester+united+jersey&_sacat=0",
            ("Madrid", "jerseys"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+real+madrid+jersey&_sacat=0",
            ("Juventus", "jerseys"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+juventus+jersey&_sacat=0",
            ("Portugal", "jerseys"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+portugal+jersey&_sacat=0",
            ("Al-Nassr", "jerseys"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+al+nassr+jersey&_sacat=0",
            ("General", "memorabilia"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+memorabilia&_sacat=0",
            ("General", "signed_items"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+signed&_sacat=0",
            ("General", "boots"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+boots+shoes&_sacat=0",
            ("General", "cards"): "https://www.ebay.com/sch/i.html?_nkw=cristiano+ronaldo+trading+card&_sacat=0",
        }
        
        for (era, category), url in searches.items():
            yield scrapy.Request(url, self.parse, cb_kwargs={'era': era, 'category': category})

    def parse(self, response, era, category):
        for item in response.css("ul.srp-results .s-item"):
            title = item.css("div.s-item__title span::text").get()
            price = item.css("span.s-item__price::text").get()
            link = item.css("a.s-item__link::attr(href)").get()
            image_url = item.css("div.s-item__image-wrapper img::attr(data-defer-load)").get() or item.css("div.s-item__image-wrapper img::attr(src)").get()

            if title and price and link and image_url:
                if "Sponsored" in title:
                    continue

                price_str = price.replace("$", "").replace(",", "").strip()
                try:
                    price_float = float(price_str)
                except ValueError:
                    price_float = 0.0

                if "s-l64" in image_url:
                    image_url = image_url.replace("s-l64", "s-l400")

                # Extract team and year from title if possible
                team = self._extract_team(title, era)
                year = self._extract_year(title)
                size = self._extract_size(title)
                condition = self._extract_condition(title)

                yield {
                    "title_en": title,
                    "price": price_float,
                    "item_url": link,
                    "img_url": image_url,
                    "era": era,
                    "category": category,
                    "team": team,
                    "year": year,
                    "size": size,
                    "condition": condition,
                    "source": "eBay",
                    "description_en": f"Cristiano Ronaldo {category.replace('_', ' ')} from {era} era. {title}",
                    "description_he": f"פריט של כריסטיאנו רונאלדו מתקופת {era}. {title}",
                }

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
        elif re.search(r'\b(vintage|retro)\b', title.lower()):
            return "Vintage"
        return "Unknown"
