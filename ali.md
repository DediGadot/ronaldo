# AliExpress Integration Tasks

## Atomic Task List

1. **Pipeline Integration**  
   Modify `app/pipelines.py` to process AliExpress items with same logic as eBay items

2. **API Updates**  
   Update `app/api.py` to:
   - Fetch parts from both sources
   - Add result shuffling logic

3. **Frontend Components**  
   Update `frontend/src/App.jsx` and `PartCard.jsx` to:
   - Handle mixed part sources
   - Display source indicators

4. **Database Schema**  
   Update `app/models.py`:
   - Add new source type
   - Add proper indexing

5. **Scheduler Update**  
   Modify `run_app.sh` to include AliExpress spider in scraping schedule

6. **Shuffling Algorithm**  
   Create utility function in `app/utils.py` for:
   - Combining results
   - Fair shuffling logic