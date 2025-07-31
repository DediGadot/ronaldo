from app.database import SessionLocal, engine
from app.models import Item, Part
from app.crud import create_item, create_part

class RonaldoItemsPipeline:
    """Pipeline to handle Ronaldo items from multiple sources (eBay, AliExpress, Schmiedmann, etc.)"""
    
    def open_spider(self, spider):
        self.session = SessionLocal()
        self.items_processed = 0
        spider.logger.info(f"🔧 Pipeline opened for spider: {spider.name}")

    def close_spider(self, spider):
        spider.logger.info(f"✅ Pipeline processed {self.items_processed} items for {spider.name}")
        self.session.close()

    def process_item(self, item, spider):
        try:
            # Check if this is a new Item or legacy Part format
            has_item_url = 'item_url' in item
            has_era_or_category = 'era' in item or 'category' in item
            
            if has_item_url or has_era_or_category:
                # This is a new Ronaldo item format
                return self._process_ronaldo_item(item, spider)
            else:
                # This is legacy Part format - convert or handle separately
                return self._process_legacy_part(item, spider)
            
        except Exception as e:
            spider.logger.error(f"❌ Error processing item: {e} - Item: {item}")
            # Return item anyway to not break the pipeline
            return item

    def _process_ronaldo_item(self, item, spider):
        """Process new Ronaldo item format"""
        # Validate required fields for Ronaldo items
        required_fields = ['title_en', 'price', 'source']
        missing_fields = [field for field in required_fields if not item.get(field)]
        
        if missing_fields:
            spider.logger.warning(f"⚠️ Ronaldo item missing required fields {missing_fields}: {item}")
            return item
        
        # Ensure price is valid
        if item.get('price', 0) <= 0:
            spider.logger.warning(f"⚠️ Ronaldo item has invalid price: {item}")
            return item
        
        # Set default item_url if not present
        if not item.get('item_url'):
            item['item_url'] = item.get('ebay_url', f"https://example.com/item/{hash(item.get('title_en', ''))}")
        
        # Log item details
        source = item.get('source', 'Unknown')
        title = item.get('title_en', 'Unknown Title')[:50]
        price = item.get('price', 0)
        era = item.get('era', 'Unknown')
        category = item.get('category', 'Unknown')
        spider.logger.debug(f"💾 Processing {source} Ronaldo item: {title}... (${price}) [{era}/{category}]")
        
        # Create item in database
        created_item = create_item(self.session, item)
        self.items_processed += 1
        
        return item

    def _process_legacy_part(self, item, spider):
        """Process legacy Part format for backward compatibility"""
        # Validate required fields
        required_fields = ['title_en', 'price', 'source']
        missing_fields = [field for field in required_fields if not item.get(field)]
        
        if missing_fields:
            spider.logger.warning(f"⚠️ Legacy part missing required fields {missing_fields}: {item}")
            return item
        
        # Ensure price is valid
        if item.get('price', 0) <= 0:
            spider.logger.warning(f"⚠️ Legacy part has invalid price: {item}")
            return item
        
        # Log item details
        source = item.get('source', 'Unknown')
        title = item.get('title_en', 'Unknown Title')[:50]
        price = item.get('price', 0)
        spider.logger.debug(f"💾 Processing {source} legacy part: {title}... (${price})")
        
        # Create part in database (legacy)
        created_part = create_part(self.session, item)
        self.items_processed += 1
        
        return item

# Keep the old names for backward compatibility
class MultiSourceScraperPipeline(RonaldoItemsPipeline):
    """Backward compatibility alias for the Ronaldo items pipeline"""
    pass

class EbayScraperPipeline(RonaldoItemsPipeline):
    """Backward compatibility alias for the Ronaldo items pipeline"""
    pass
