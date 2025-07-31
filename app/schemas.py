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
