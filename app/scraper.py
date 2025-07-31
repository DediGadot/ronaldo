from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import scrapy
from .spiders.ebay_spider import EbaySpider
from .database import SessionLocal
from . import crud
from .translation import PartTranslator

def run_spider():
    process = CrawlerProcess(get_project_settings())
    results = []

    def crawler_results(item, response, spider):
        results.append(item)

    crawler = process.create_crawler(EbaySpider)
    crawler.signals.connect(crawler_results, signal=scrapy.signals.item_scraped)
    process.crawl(crawler)
    process.start()
    return results

def scrape_and_store():
    translator = PartTranslator()
    db = SessionLocal()
    
    try:
        items = run_spider()
        stored_items = []
        for item in items:
            if crud.get_part_by_ebay_url(db, ebay_url=item['ebay_url']):
                continue

            title_he = translator.translate(item['title_en'])

            part_data = {
                "title_en": item['title_en'],
                "title_he": title_he,
                "price": item['price'],
                "ebay_url": item['ebay_url'],
                "img_url": item['img_url'],
            }
            
            crud.create_part(db, part_data=part_data)
            stored_items.append(part_data)
        return stored_items
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting scraper...")
    results = scrape_and_store()
    print(f"Scraped and stored {len(results)} new items.")