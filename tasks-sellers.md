# Project Tasks: Add New Part Sellers

This document outlines the atomic tasks required to expand the application by integrating additional car part sellers. The goal is to provide users with a wider selection of parts from reputable sources beyond eBay.

---

### Tools & Libraries Documentation
*For any of the libraries mentioned below, you can use the `Context7` tools to find relevant documentation and code examples.*
- `resolve-library-id libraryName="<library>"`
- `get-library-docs context7CompatibleLibraryID="<id>"`

---

## Phase 1: Core Refactoring for Multi-Source Support

### Task 1.1: Database Schema Update
- [ ] **Modify `app/models.py`:** Add a `source` column to the `Part` table (e.g., `source = Column(String, index=True)`). This will store the name of the seller (e.g., "eBay", "FCP Euro").
- [ ] **Update Database Creation:** Ensure the `create_tables.py` script reflects this change. The database will need to be recreated.

### Task 1.2: API and Schema Updates
- [ ] **Modify `app/schemas.py`:** Add the `source` field to the `Part` Pydantic schema so it's included in API responses.
- [ ] **Modify `app/api.py`:** Update the `GET /api/parts/` endpoint to allow filtering by the new `source` field. This should accept a list of sources as a query parameter.

### Task 1.3: Scraper Orchestration
- [ ] **Modify Scrapy `settings.py`:** Update `ITEM_PIPELINES` if necessary to handle items coming from different spiders.
- [ ] **Update `run_app.sh`:** Modify the script to run all spiders when scraping data. The `scrapy crawl` command can run multiple spiders sequentially (e.g., `scrapy crawl ebay && scrapy crawl fcpeuro`).

---

## Phase 2: Implement New Scrapers (Parallel Tasks)

For each new seller, a dedicated spider needs to be created. These tasks can be worked on in parallel.

### Task 2.1: FCP Euro Integration
- [ ] **Create Spider:** Create a new file `app/spiders/fcpeuro_spider.py`.
- [ ] **Analyze Website:** Manually inspect `fcpeuro.com` for BMW E28 parts to identify the correct search URL structure and the CSS selectors for part title, price, image, and product URL.
- [ ] **Implement Spider Logic:** Write the Scrapy spider to:
    - Target the correct search URL.
    - Parse the product listings.
    - Follow links to individual product pages to extract detailed descriptions.
    - Yield a structured item including `source: 'FCP Euro'`.
- [ ] **Handle Anti-Scraping:** Implement User-Agent rotation and respectful request intervals (`DOWNLOAD_DELAY`).

### Task 2.2: RockAuto Integration
- [ ] **Create Spider:** Create a new file `app/spiders/rockauto_spider.py`.
- [ ] **Analyze Website:** Inspect `rockauto.com`. Their site is notoriously difficult to scrape due to its heavy reliance on JavaScript and complex UI. This may require a different approach, potentially using a headless browser like Playwright integrated with Scrapy if simple `httpx` requests fail.
- [ ] **Implement Spider Logic:** Write the spider to navigate the catalog to the BMW E28 section and extract part details.
    - Yield a structured item including `source: 'RockAuto'`.
- [ ] **Handle Anti-Scraping:** This will likely be the most challenging. Be prepared for advanced anti-bot measures.

### Task 2.3: Turner Motorsport Integration
- [ ] **Create Spider:** Create a new file `app/spiders/turner_spider.py`.
- [ ] **Analyze Website:** Inspect `turnermotorsport.com` for their BMW E28 parts section. Identify CSS selectors for part details.
- [ ] **Implement Spider Logic:** Write the spider to parse their product listings.
    - Yield a structured item including `source: 'Turner Motorsport'`.
- [ ] **Handle Anti-Scraping:** Implement standard politeness policies.

### Task 2.4: Autodoc Integration
- [ ] **Create Spider:** Create a new file `app/spiders/autodoc_spider.py`.
- [ ] **Analyze Website:** Inspect `autodoc.co.uk` for their BMW E28 parts section. Identify the necessary CSS selectors.
- [ ] **Implement Spider Logic:** Write the spider to scrape their catalog.
    - Yield a structured item including `source: 'Autodoc'`.
- [ ] **Handle Anti-Scraping:** Implement standard politeness policies.

---

## Phase 3: Frontend Enhancements

### Task 3.1: Update Part Card UI
- [ ] **Modify `frontend/src/components/PartCard.jsx`:** Add a small, styled badge or label to each card that displays the `source` of the part (e.g., a small logo or text like "From eBay").

### Task 3.2: Implement Filtering
- [ ] **Modify `frontend/src/App.jsx`:**
    - Add state to manage selected sources.
    - Create a filter UI (e.g., a set of checkboxes) that allows users to toggle which sellers they want to see results from.
    - Update the API fetch call to include the selected sources as query parameters.

---

## Phase 4: Testing and Validation

### Task 4.1: Unit Tests for New Scrapers
- [ ] For each new spider, create a corresponding test file in the `tests/` directory.
- [ ] Save static HTML fixtures from each seller's website to `tests/fixtures/`.
- [ ] Write unit tests that run the spider on the static HTML and verify that the data is parsed correctly.

### Task 4.2: API Test Updates
- [ ] **Modify `tests/test_api.py`:** Add tests for the new `source` filtering functionality on the `/api/parts/` endpoint.

### Task 4.3: Manual Validation
- [ ] Run the full application using `./run_app.sh`.
- [ ] Verify that data from all new sellers is displayed correctly.
- [ ] Test the frontend filtering functionality to ensure it works as expected.
