# Project Tasks: Add AliExpress Scraper

This document outlines the atomic tasks required to expand the application by integrating AliExpress as a new car part seller. The goal is to provide users with parts from AliExpress alongside eBay parts, with all parts displayed shuffled in the UI.

---

## Phase 1: Core Refactoring for Multi-Source Support

### Task 1.1: Database Schema Update
- [ ] **Modify `app/models.py`:** 
  - Add a `source` column to the `Part` table (e.g., `source = Column(String, index=True, default="eBay")`).
  - Add a unique constraint on a combination of fields to prevent duplicates across sources.
- [ ] **Update Database Creation:** 
  - Ensure the `create_tables.py` script reflects this change.
  - Note that the database will need to be recreated or migrated.

### Task 1.2: API and Schema Updates
- [ ] **Modify `app/schemas.py`:** 
  - Add the `source` field to the `Part` Pydantic schema so it's included in API responses.
- [ ] **Modify `app/api.py`:** 
  - Update the `GET /api/parts/` endpoint to allow filtering by the new `source` field.
  - Add a parameter to shuffle results when fetching parts from multiple sources.

### Task 1.3: Scraper Orchestration
- [ ] **Modify Scrapy `settings.py`:** 
  - Update `ITEM_PIPELINES` if necessary to handle items coming from different spiders.
- [ ] **Update `run_app.sh`:** 
  - Modify the script to run all spiders when scraping data.
  - The `scrapy crawl` command can run multiple spiders sequentially (e.g., `scrapy crawl ebay && scrapy crawl aliexpress`).

---

## Phase 2: Implement AliExpress Scraper

### Task 2.1: AliExpress Integration
- [ ] **Create Spider:** 
  - Create a new file `app/spiders/aliexpress_spider.py`.
- [ ] **Analyze Website:** 
  - Manually inspect `aliexpress.com` for BMW E28 parts to identify the correct search URL structure and the CSS selectors for part title, price, image, and product URL.
- [ ] **Implement Spider Logic:** 
  - Write the Scrapy spider to:
    - Target the correct search URL for BMW E28 parts.
    - Parse the product listings.
    - Yield a structured item including `source: 'AliExpress'`.
- [ ] **Handle Anti-Scraping:** 
  - Implement User-Agent rotation and respectful request intervals (`DOWNLOAD_DELAY`).
  - Handle potential JavaScript-heavy pages if needed.

---

## Phase 3: Data Processing Updates

### Task 3.1: Update Pipeline
- [ ] **Modify `app/pipelines.py`:** 
  - Update the pipeline to handle the `source` field when saving items.
  - Ensure items from different sources are properly identified.

### Task 3.2: Update CRUD Operations
- [ ] **Modify `app/crud.py`:** 
  - Update functions to handle the new `source` field.
  - Add functionality to fetch parts from multiple sources and shuffle them.

---

## Phase 4: API Updates

### Task 4.1: Update API Endpoints
- [ ] **Modify `app/api.py`:** 
  - Update the parts endpoint to fetch from all sources and shuffle results by default.
  - Add filtering options for specific sources.

---

## Phase 5: Frontend Enhancements

### Task 5.1: Update Part Card UI
- [ ] **Modify `frontend/src/components/PartCard.jsx`:** 
  - Add a small, styled badge or label to each card that displays the `source` of the part (e.g., "From AliExpress").

### Task 5.2: Update Main App Component
- [ ] **Modify `frontend/src/App.jsx`:** 
  - Update the API fetch call to get parts from all sources.
  - Remove the series filter buttons if no longer needed or update them to work with shuffled results.

---

## Phase 6: Testing and Validation

### Task 6.1: Unit Tests for New Scraper
- [ ] **Create Test File:** 
  - Create `tests/test_aliexpress_spider.py`.
- [ ] **Save Fixtures:** 
  - Save static HTML fixtures from AliExpress to `tests/fixtures/`.
- [ ] **Write Unit Tests:** 
  - Write unit tests that run the spider on the static HTML and verify that the data is parsed correctly.

### Task 6.2: API Test Updates
- [ ] **Modify `tests/test_api.py`:** 
  - Add tests for the updated parts endpoint functionality.

### Task 6.3: Manual Validation
- [ ] **Run Full Application:** 
  - Run the full application using `./run_app.sh`.
- [ ] **Verify Data Display:** 
  - Verify that data from both eBay and AliExpress is displayed correctly and shuffled.
- [ ] **Test Filtering:** 
  - Test any filtering functionality to ensure it works as expected.