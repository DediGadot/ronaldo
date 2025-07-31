from app.database import SessionLocal
from app.models import Part
from app.crud import create_part

# Test creating a part with the updated model
test_part_data = {
    "title_en": "Test BMW E28 Part",
    "title_he": "בדיקה BMW E28",
    "price": 123.45,
    "img_url": "https://example.com/image.jpg",
    "ebay_url": "https://example.com/product",
    "series": "E28",
    "source": "Test",
    "description_en": "Test description",
    "description_he": "בדיקה תיאור"
}

db = SessionLocal()
try:
    part = create_part(db, test_part_data)
    print(f"Successfully created part with ID: {part.id}")
    
    # Retrieve the part
    retrieved_part = db.query(Part).filter(Part.id == part.id).first()
    print(f"Retrieved part: {retrieved_part.title_en} from {retrieved_part.source}")
    
    # Check all parts
    all_parts = db.query(Part).all()
    print(f"Total parts in database: {len(all_parts)}")
    
finally:
    db.close()