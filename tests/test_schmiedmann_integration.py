import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.api import get_db
from app.models import Part
from datetime import datetime

# Create test database for Schmiedmann integration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_schmiedmann.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Set up test database with Schmiedmann sample data."""
    Base.metadata.create_all(bind=engine)
    
    # Add sample parts including Schmiedmann parts
    db = TestingSessionLocal()
    try:
        sample_parts = [
            # eBay parts
            Part(
                title_en="BMW E28 Brake Pad",
                title_he="רפידות בלם BMW E28",
                price=45.99,
                img_url="https://example.com/brake-pad.jpg",
                ebay_url="https://ebay.com/item/123",
                series="E28",
                source="eBay",
                description_en="High quality brake pad for BMW E28",
                description_he="רפידות בלם איכותיות עבור BMW E28",
                fetched_at=datetime.now()
            ),
            # AliExpress parts
            Part(
                title_en="BMW E28 Oil Filter",
                title_he="מסנן שמן BMW E28",
                price=25.50,
                img_url="https://example.com/oil-filter.jpg",
                ebay_url="https://aliexpress.com/item/456",
                series="E28",
                source="AliExpress",
                description_en="Oil filter for BMW E28 from AliExpress",
                description_he="מסנן שמן עבור BMW E28 מ-AliExpress",
                fetched_at=datetime.now()
            ),
            # Schmiedmann parts
            Part(
                title_en="BMW E28 M5 Brake Disc Set - Schmiedmann",
                title_he="סט דיסקי בלמים BMW E28 M5 - Schmiedmann",
                price=97.19,  # €89.99 * 1.08
                img_url="https://example.com/schmiedmann-brake-disc.jpg",
                ebay_url="https://www.schmiedmann.com/en/bmw-E28/brake-disc-set",
                series="E28",
                source="Schmiedmann",
                description_en="BMW E28 part from Schmiedmann: BMW E28 M5 Brake Disc Set",
                description_he="חלק BMW E28 מ-Schmiedmann: BMW E28 M5 Brake Disc Set",
                fetched_at=datetime.now()
            ),
            Part(
                title_en="BMW F10 M Performance Carbon Fiber Spoiler",
                title_he="ספויילר מסיבי פחמן BMW F10 M Performance",
                price=323.99,  # €299.99 * 1.08
                img_url="https://example.com/schmiedmann-spoiler.jpg",
                ebay_url="https://www.schmiedmann.com/en/bmw-f10/carbon-spoiler",
                series="F10",
                source="Schmiedmann",
                description_en="BMW F10 part from Schmiedmann: M Performance Carbon Fiber Spoiler",
                description_he="חלק BMW F10 מ-Schmiedmann: M Performance Carbon Fiber Spoiler",
                fetched_at=datetime.now()
            ),
            # Additional F10 eBay part for testing
            Part(
                title_en="BMW F10 Air Filter",
                title_he="מסנן אוויר BMW F10",
                price=35.00,
                img_url="https://example.com/air-filter.jpg",
                ebay_url="https://ebay.com/item/789",
                series="F10",
                source="eBay",
                description_en="Air filter for BMW F10",
                description_he="מסנן אוויר עבור BMW F10",
                fetched_at=datetime.now()
            )
        ]
        
        for part in sample_parts:
            db.add(part)
        db.commit()
        
    finally:
        db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

def test_get_parts_with_schmiedmann_source_filter():
    """Test getting parts filtered by Schmiedmann source."""
    response = client.get("/api/parts/?source=Schmiedmann")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 2  # Should return only Schmiedmann parts
    
    # Verify all returned parts are from Schmiedmann
    for part in parts:
        assert part['source'] == 'Schmiedmann'
        assert 'schmiedmann.com' in part['ebay_url']
        assert 'Schmiedmann' in part['description_en']

def test_get_parts_all_sources_include_schmiedmann():
    """Test getting all parts includes Schmiedmann parts."""
    response = client.get("/api/parts/")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 5  # Should return all 5 parts
    
    # Verify we have parts from all three sources
    sources = {part['source'] for part in parts}
    assert 'eBay' in sources
    assert 'AliExpress' in sources
    assert 'Schmiedmann' in sources

def test_get_parts_e28_series_with_schmiedmann():
    """Test getting E28 parts includes Schmiedmann E28 parts."""
    response = client.get("/api/parts/?series=E28")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 3  # E28 parts from all sources
    
    # Verify we have E28 parts from different sources including Schmiedmann
    sources = {part['source'] for part in parts}
    assert 'Schmiedmann' in sources
    
    # Find the Schmiedmann E28 part
    schmiedmann_part = next(part for part in parts if part['source'] == 'Schmiedmann')
    assert schmiedmann_part['series'] == 'E28'
    assert 'M5 Brake Disc Set' in schmiedmann_part['title_en']

def test_get_parts_f10_series_with_schmiedmann():
    """Test getting F10 parts includes Schmiedmann F10 parts."""
    response = client.get("/api/parts/?series=F10")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 2  # F10 parts from eBay and Schmiedmann
    
    # Find the Schmiedmann F10 part
    schmiedmann_parts = [part for part in parts if part['source'] == 'Schmiedmann']
    assert len(schmiedmann_parts) == 1
    
    schmiedmann_part = schmiedmann_parts[0]
    assert schmiedmann_part['series'] == 'F10'
    assert 'Carbon Fiber Spoiler' in schmiedmann_part['title_en']
    assert schmiedmann_part['price'] == 323.99  # Converted EUR price

def test_get_parts_combined_series_and_schmiedmann_filter():
    """Test filtering by both series and Schmiedmann source."""
    response = client.get("/api/parts/?series=E28&source=Schmiedmann")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 1  # Should return only E28 Schmiedmann parts
    
    part = parts[0]
    assert part['series'] == 'E28'
    assert part['source'] == 'Schmiedmann'
    assert 'M5 Brake Disc Set' in part['title_en']

def test_schmiedmann_parts_have_correct_fields():
    """Test that Schmiedmann parts have all required fields."""
    response = client.get("/api/parts/?source=Schmiedmann")
    assert response.status_code == 200
    
    parts = response.json()
    
    for part in parts:
        # Check required fields
        assert 'id' in part
        assert 'title_en' in part
        assert 'price' in part
        assert 'img_url' in part
        assert 'ebay_url' in part
        assert 'series' in part
        assert 'source' in part
        assert 'fetched_at' in part
        
        # Verify Schmiedmann-specific properties
        assert part['source'] == 'Schmiedmann'
        assert part['series'] in ['E28', 'F10']
        assert part['price'] > 0
        assert 'Schmiedmann' in part['description_en']
        assert 'schmiedmann.com' in part['ebay_url']

def test_schmiedmann_price_conversion():
    """Test that Schmiedmann prices are properly converted from EUR to USD."""
    response = client.get("/api/parts/?source=Schmiedmann")
    assert response.status_code == 200
    
    parts = response.json()
    
    # Find the E28 brake disc (originally €89.99)
    brake_disc_part = next(part for part in parts if 'Brake Disc' in part['title_en'])
    assert brake_disc_part['price'] == 97.19  # €89.99 * 1.08
    
    # Find the F10 spoiler (originally €299.99)
    spoiler_part = next(part for part in parts if 'Spoiler' in part['title_en'])
    assert spoiler_part['price'] == 323.99  # €299.99 * 1.08

def test_pagination_with_schmiedmann_parts():
    """Test pagination works correctly with Schmiedmann parts."""
    # Test with limit
    response = client.get("/api/parts/?source=Schmiedmann&limit=1")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 1
    assert parts[0]['source'] == 'Schmiedmann'
    
    # Test with skip
    response = client.get("/api/parts/?source=Schmiedmann&skip=1&limit=1")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 1
    assert parts[0]['source'] == 'Schmiedmann'

def test_get_single_schmiedmann_part():
    """Test getting a single Schmiedmann part by ID."""
    # First get all Schmiedmann parts to find an ID
    response = client.get("/api/parts/?source=Schmiedmann")
    parts = response.json()
    assert len(parts) > 0
    
    part_id = parts[0]['id']
    
    # Get single part
    response = client.get(f"/api/parts/{part_id}")
    assert response.status_code == 200
    
    part = response.json()
    assert part['id'] == part_id
    assert part['source'] == 'Schmiedmann'
    assert 'schmiedmann.com' in part['ebay_url']