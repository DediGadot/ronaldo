import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.api import get_db
from app.models import Part
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
    """Set up test database with sample data."""
    Base.metadata.create_all(bind=engine)
    
    # Add sample parts for testing
    db = TestingSessionLocal()
    try:
        sample_parts = [
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
                fetched_at=datetime.utcnow()
            ),
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
                fetched_at=datetime.utcnow()
            ),
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
                fetched_at=datetime.utcnow()
            ),
            Part(
                title_en="BMW F10 Spark Plug",
                title_he="נר ההתנה BMW F10",
                price=15.99,
                img_url="https://example.com/spark-plug.jpg",
                ebay_url="https://aliexpress.com/item/101112",
                series="F10",
                source="AliExpress",
                description_en="Spark plug for BMW F10 from AliExpress",
                description_he="נר התנה עבור BMW F10 מ-AliExpress",
                fetched_at=datetime.utcnow()
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

def test_get_parts_without_any_filter():
    """Test getting all parts without any filters."""
    response = client.get("/api/parts/")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 4  # Should return all parts
    
    # Verify we have parts from both sources
    sources = [part['source'] for part in parts]
    assert 'eBay' in sources
    assert 'AliExpress' in sources

def test_get_parts_with_ebay_source_filter():
    """Test getting parts filtered by eBay source."""
    response = client.get("/api/parts/?source=eBay")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 2  # Should return only eBay parts
    
    # Verify all returned parts are from eBay
    for part in parts:
        assert part['source'] == 'eBay'
        assert 'ebay.com' in part['ebay_url']

def test_get_parts_with_aliexpress_source_filter():
    """Test getting parts filtered by AliExpress source."""
    response = client.get("/api/parts/?source=AliExpress")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 2  # Should return only AliExpress parts
    
    # Verify all returned parts are from AliExpress
    for part in parts:
        assert part['source'] == 'AliExpress'
        assert 'aliexpress.com' in part['ebay_url']

def test_get_parts_with_series_filter_only():
    """Test getting parts filtered by series only."""
    response = client.get("/api/parts/?series=E28")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 2  # Should return only E28 parts
    
    # Verify all returned parts are for E28
    for part in parts:
        assert part['series'] == 'E28'

def test_get_parts_with_series_and_source_filter():
    """Test getting parts with both series and source filters."""
    response = client.get("/api/parts/?series=E28&source=eBay")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 1  # Should return only E28 eBay parts
    
    part = parts[0]
    assert part['series'] == 'E28'
    assert part['source'] == 'eBay'
    assert part['title_en'] == 'BMW E28 Brake Pad'

def test_get_parts_with_f10_and_aliexpress_filter():
    """Test getting F10 parts from AliExpress."""
    response = client.get("/api/parts/?series=F10&source=AliExpress")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 1  # Should return only F10 AliExpress parts
    
    part = parts[0]
    assert part['series'] == 'F10'
    assert part['source'] == 'AliExpress'
    assert part['title_en'] == 'BMW F10 Spark Plug'

def test_get_parts_with_nonexistent_source():
    """Test filtering by a nonexistent source."""
    response = client.get("/api/parts/?source=NonExistentSource")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 0  # Should return no parts

def test_get_parts_with_nonexistent_series():
    """Test filtering by a nonexistent series."""
    response = client.get("/api/parts/?series=E30")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 0  # Should return no parts

def test_get_parts_with_skip_and_limit():
    """Test pagination with skip and limit parameters."""
    # Test skip=1, limit=2
    response = client.get("/api/parts/?skip=1&limit=2")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 2  # Should return 2 parts
    
    # Test with source filter and pagination
    response = client.get("/api/parts/?source=eBay&skip=0&limit=1")
    assert response.status_code == 200
    
    parts = response.json()
    assert len(parts) == 1  # Should return 1 eBay part
    assert parts[0]['source'] == 'eBay'

def test_get_single_part():
    """Test getting a single part by ID."""
    # First get all parts to find a valid ID
    response = client.get("/api/parts/")
    parts = response.json()
    assert len(parts) > 0
    
    part_id = parts[0]['id']
    
    # Get single part
    response = client.get(f"/api/parts/{part_id}")
    assert response.status_code == 200
    
    part = response.json()
    assert part['id'] == part_id
    assert 'source' in part
    assert 'series' in part

def test_get_nonexistent_part():
    """Test getting a part that doesn't exist."""
    response = client.get("/api/parts/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Part not found"}

def test_parts_have_required_fields():
    """Test that all parts have the required fields including source."""
    response = client.get("/api/parts/")
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
        assert 'source' in part  # This is the new field we added
        assert 'fetched_at' in part
        
        # Verify source is valid
        assert part['source'] in ['eBay', 'AliExpress']
        
        # Verify series is valid
        assert part['series'] in ['E28', 'F10']