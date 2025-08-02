from sqlalchemy import Column, Integer, String, DateTime, Float
from .database import Base
import datetime
from pydantic import BaseModel

class ItemBase(BaseModel):
    title_en: str
    title_he: str
    price: float
    img_url: str
    item_url: str
    source: str = "eBay"

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    fetched_at: datetime.datetime
    data_age_seconds: int

    class Config:
        from_attributes = True

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title_en = Column(String, index=True)
    title_he = Column(String, index=True)
    price = Column(Float)
    img_url = Column(String)
    item_url = Column(String, unique=True)
    era = Column(String, index=True)  # Ronaldo career periods: Sporting, United, Madrid, Juventus, Portugal, Al-Nassr
    category = Column(String, index=True)  # jerseys, boots, memorabilia, collectibles, signed_items, cards
    source = Column(String, index=True, default="eBay")
    description_en = Column(String)
    description_he = Column(String)
    size = Column(String)  # For clothing items
    condition = Column(String)  # New, Used, Vintage, etc.
    authenticity = Column(String)  # Verified, Unverified, COA (Certificate of Authenticity)
    year = Column(String)  # Year of item/season
    team = Column(String)  # Sporting CP, Manchester United, Real Madrid, Juventus, Portugal, Al-Nassr
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)

# Ronaldo Stories and Facts
class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title_en = Column(String, index=True)
    title_he = Column(String, index=True)
    content_en = Column(String)  # Full story content
    content_he = Column(String)  # Hebrew translation
    summary_en = Column(String)  # Brief summary for collapsed view
    summary_he = Column(String)  # Hebrew summary
    story_type = Column(String, index=True)  # milestone, record, personal, quote, trivia, match
    era = Column(String, index=True)  # Associated era (can be null for general stories)
    team = Column(String, index=True)  # Associated team
    year = Column(String)  # Year of the event
    category_relevance = Column(String)  # Which item categories this relates to
    media_url = Column(String)  # Optional image/video URL
    source_url = Column(String)  # Source of the information
    importance_score = Column(Integer, default=5)  # 1-10 for sorting/filtering
    related_search_terms = Column(String)  # Comma-separated terms for finding related items
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Keep Part class for backward compatibility during migration
class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    title_en = Column(String, index=True)
    title_he = Column(String, index=True)
    price = Column(Float)
    img_url = Column(String)
    ebay_url = Column(String, unique=True)
    series = Column(String, index=True)
    source = Column(String, index=True, default="eBay")
    description_en = Column(String)
    description_he = Column(String)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
