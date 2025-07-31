from app.database import SessionLocal
from app.models import Part
from app import crud, utils
from collections import defaultdict

def test_shuffle():
    db = SessionLocal()
    try:
        # Get all parts
        all_parts = crud.get_parts(db)
        print(f'Total parts: {len(all_parts)}')
        
        # Group by source
        parts_by_source = defaultdict(list)
        for part in all_parts:
            parts_by_source[part.source].append(part)
        
        print('Parts by source:')
        for source, parts in parts_by_source.items():
            print(f'  {source}: {len(parts)} parts')
            for part in parts:
                print(f'    - {part.title_en}')
        
        # Test shuffle function
        shuffled = utils.shuffle_multiple_sources(parts_by_source)
        print(f'\nShuffled parts: {len(shuffled)}')
        print('Shuffled order:')
        for i, part in enumerate(shuffled):
            print(f'  {i+1}. {part.title_en} ({part.source})')
            
    finally:
        db.close()

if __name__ == "__main__":
    test_shuffle()