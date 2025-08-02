from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# New Item endpoints
@app.get("/items/", response_model=list[schemas.Item])
def read_items(era: str | None = None, category: str | None = None, source: str | None = None, team: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, era=era, category=category, source=source, team=team, skip=skip, limit=limit)
    return items


@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


# Legacy Part endpoints (for backward compatibility)
@app.get("/parts/", response_model=list[schemas.Part])
def read_parts(series: str | None = None, source: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    parts = crud.get_parts(db, series=series, source=source, skip=skip, limit=limit)
    return parts


@app.get("/parts/{part_id}", response_model=schemas.Part)
def read_part(part_id: int, db: Session = Depends(get_db)):
    db_part = crud.get_part(db, part_id=part_id)
    if db_part is None:
        raise HTTPException(status_code=404, detail="Part not found")
    return db_part


# Story endpoints
@app.get("/stories/", response_model=list[schemas.Story])
def read_stories(era: str | None = None, team: str | None = None, story_type: str | None = None, 
                 category: str | None = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    # Try to get stories from database
    stories = crud.get_stories(db, era=era, team=team, story_type=story_type, skip=skip, limit=limit)
    
    # If no stories found and filters are applied, generate some using AI
    if len(stories) < 5 and (era or team or category):
        from .story_generator import get_or_generate_stories
        stories = get_or_generate_stories(era=era, category=category, team=team, limit=limit)
    
    return stories


@app.get("/stories/{story_id}", response_model=schemas.Story)
def read_story(story_id: int, db: Session = Depends(get_db)):
    db_story = crud.get_story(db, story_id=story_id)
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return db_story


@app.post("/stories/generate")
def generate_stories(era: str | None = None, category: str | None = None, team: str | None = None):
    """Endpoint to manually trigger story generation"""
    from .story_generator import generate_contextual_stories
    
    generated = generate_contextual_stories(era=era, category=category, team=team, count=5)
    return {"generated": len(generated), "stories": generated}
