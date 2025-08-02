from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    title_en: str
    price: float
    img_url: str
    item_url: str
    source: str = "eBay"

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    era: str | None = None
    category: str | None = None
    title_he: str | None = None
    description_en: str | None = None
    description_he: str | None = None
    size: str | None = None
    condition: str | None = None
    authenticity: str | None = None
    year: str | None = None
    team: str | None = None
    fetched_at: datetime

    class Config:
        from_attributes = True

# Story Schemas
class StoryBase(BaseModel):
    title_en: str
    title_he: str | None = None
    content_en: str
    content_he: str | None = None
    summary_en: str
    summary_he: str | None = None
    story_type: str  # milestone, record, personal, quote, trivia, match
    era: str | None = None
    team: str | None = None
    year: str | None = None
    category_relevance: str | None = None
    media_url: str | None = None
    source_url: str | None = None
    importance_score: int = 5
    related_search_terms: str | None = None

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Keep Part schemas for backward compatibility during migration
class PartBase(BaseModel):
    title_en: str
    price: float
    img_url: str
    ebay_url: str
    source: str = "eBay"

class PartCreate(PartBase):
    pass

class Part(PartBase):
    id: int
    series: str
    title_he: str | None = None
    description_en: str | None = None
    description_he: str | None = None
    fetched_at: datetime

    class Config:
        from_attributes = True
