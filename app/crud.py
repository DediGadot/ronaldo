from sqlalchemy.orm import Session
from . import models

# New Item CRUD operations
def get_item_by_url(db: Session, item_url: str):
    return db.query(models.Item).filter(models.Item.item_url == item_url).first()

def create_item(db: Session, item_data: dict):
    # Check if item with this URL already exists
    existing_item = get_item_by_url(db, item_data.get('item_url', ''))
    if existing_item:
        # Update existing item with new data
        for key, value in item_data.items():
            if hasattr(existing_item, key):
                setattr(existing_item, key, value)
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    # Create new item
    db_item = models.Item(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items(db: Session, era: str | None = None, category: str | None = None, source: str | None = None, team: str | None = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Item)
    if era:
        query = query.filter(models.Item.era == era)
    if category:
        query = query.filter(models.Item.category == category)
    if source:
        query = query.filter(models.Item.source == source)
    if team:
        query = query.filter(models.Item.team == team)
    return query.offset(skip).limit(limit).all()

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

# Legacy Part CRUD operations (for backward compatibility)
def get_part_by_ebay_url(db: Session, ebay_url: str):
    return db.query(models.Part).filter(models.Part.ebay_url == ebay_url).first()

def create_part(db: Session, part_data: dict):
    # Check if part with this URL already exists
    existing_part = get_part_by_ebay_url(db, part_data.get('ebay_url', ''))
    if existing_part:
        # Update existing part with new data
        for key, value in part_data.items():
            if hasattr(existing_part, key):
                setattr(existing_part, key, value)
        db.commit()
        db.refresh(existing_part)
        return existing_part
    
    # Create new part
    db_part = models.Part(**part_data)
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part

def get_parts(db: Session, series: str | None = None, source: str | None = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Part)
    if series:
        query = query.filter(models.Part.series == series)
    if source:
        query = query.filter(models.Part.source == source)
    return query.offset(skip).limit(limit).all()

def get_part(db: Session, part_id: int):
    return db.query(models.Part).filter(models.Part.id == part_id).first()

# Story CRUD operations
def get_story_by_title(db: Session, title_en: str):
    return db.query(models.Story).filter(models.Story.title_en == title_en).first()

def create_story(db: Session, story_data: dict):
    # Check if story with this title already exists
    existing_story = get_story_by_title(db, story_data.get('title_en', ''))
    if existing_story:
        # Update existing story with new data
        for key, value in story_data.items():
            if hasattr(existing_story, key):
                setattr(existing_story, key, value)
        db.commit()
        db.refresh(existing_story)
        return existing_story
    
    # Create new story
    db_story = models.Story(**story_data)
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

def get_stories(db: Session, era: str | None = None, team: str | None = None, 
                story_type: str | None = None, skip: int = 0, limit: int = 20):
    query = db.query(models.Story)
    if era:
        query = query.filter(models.Story.era == era)
    if team:
        query = query.filter(models.Story.team == team)
    if story_type:
        query = query.filter(models.Story.story_type == story_type)
    
    # Order by importance score descending
    query = query.order_by(models.Story.importance_score.desc())
    
    return query.offset(skip).limit(limit).all()

def get_story(db: Session, story_id: int):
    return db.query(models.Story).filter(models.Story.id == story_id).first()

def get_stories_by_filter(db: Session, era: str | None = None, team: str | None = None, limit: int = 10):
    """Helper function for story generator"""
    return get_stories(db, era=era, team=team, limit=limit)
