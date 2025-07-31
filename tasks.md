# Project Tasks: E28 Parts Scraper & API

This document outlines the atomic tasks for building the prototype, following the provided specification. The project is divided into phases, prioritizing a functional backend first, followed by the frontend and testing.

---

### Tools & Libraries Documentation
*For any of the libraries mentioned below (`fastapi`, `httpx`, `beautifulsoup4`, etc.), you can use the `Context7` tools to find relevant documentation and code examples.*
- `resolve-library-id libraryName="<library>"`
- `get-library-docs context7CompatibleLibraryID="<id>"`

---

## Phase 1: Core Backend & Scaffolding

### Task 1.1: Project Setup
- [ ] Initialize a Python project with a virtual environment.
- [ ] Create a `requirements.txt` file and add initial dependencies:
  ```
  fastapi
  uvicorn[standard]
  httpx
  beautifulsoup4
  googletrans-lite
  pydantic
  sqlalchemy
  ```
- [ ] Create the initial directory structure:
  ```
  /
  ├── app/
  │   ├── __init__.py
  │   ├── api.py          # FastAPI application
  │   ├── scraper.py      # Scraping logic
  │   ├── translation.py  # Translation logic
  │   ├── models.py       # Pydantic & DB models
  │   ├── database.py     # Database setup
  │   └── crud.py         # Database operations
  ├── static/             # For React frontend
  ├── tests/
  │   ├── __init__.py
  │   ├── fixtures/       # To store mock HTML data
  │   └── test_scraper.py
  │   └── test_api.py
  ├── terms.yaml          # Translation overrides
  └── .gitignore
  ```

### Task 1.2: Database Model (SQLite)
- [ ] In `app/database.py`, implement the SQLite database connection logic using SQLAlchemy.
- [ ] In `app/models.py`, define the `Part` SQLAlchemy model for the `parts` table with fields: `id`, `title_en`, `title_he`, `price`, `img_url`, `ebay_url`, `fetched_at`.
- [ ] Create a startup script or function to initialize the database and create the table.

---

## Phase 2: Data Scraping & Processing

### Task 2.1: Scraper Implementation
- [ ] In `app/scraper.py`, implement the async scraping function using `httpx` and `BeautifulSoup4`.
- [ ] Hard-code the eBay query URL for "BMW E28 parts" (category 6000).
- [ ] Implement logic to parse the first ~40 results, extracting `title`, `price`, `item URL`, and `thumbnail URL`.
- [ ] Implement the image URL transformation (`s-l64` → `s-l400`).
- [ ] Implement basic reliability: use a rotating desktop User-Agent and wrap requests in `asyncio.wait_for` with a 10-second timeout.

### Task 2.2: Translation & Enrichment
- [ ] Create the `terms.yaml` file for automotive term overrides.
- [ ] In `app/translation.py`, implement a function to load `terms.yaml`.
- [ ] Implement the primary translation function using `googletrans-lite`. It should first check for an override in the `terms.yaml` map before calling the translation service.

### Task 2.3: Data Persistence
- [ ] In `app/crud.py`, write functions to interact with the database (e.g., `create_part`, `get_parts`, `get_part_by_id`).
- [ ] In `app/scraper.py`, create a main orchestration script that:
    1. Fetches items from eBay.
    2. Translates titles for each item.
    3. Normalizes and cleans the data.
    4. Saves the final records to the SQLite database via `crud.py`.

---

## Phase 3: API Development

### Task 3.1: Pydantic Models
- [ ] In `app/models.py`, define Pydantic schemas for API responses (e.g., `PartResponse`) to control the output structure and add the `data_age_seconds` field.

### Task 3.2: Read-Only Endpoints
- [ ] In `app/api.py`, set up the main FastAPI application.
- [ ] Implement the `GET /v1/parts` endpoint that reads from the database using `crud.py`.
    - [ ] Add `limit` and `query` parameters (for a simple `LIKE` search on `title_he`).
- [ ] Implement the `GET /v1/parts/{part_id}` endpoint.
- [ ] Add a middleware or dependency to set the `Cache-Control: public, max-age=300` header on responses.

---

## Phase 4: Frontend Development (Prototyping)

### Task 4.1: Frontend Setup
- [ ] Initialize a React + Vite project in the `/static` directory.
- [ ] Add and configure TailwindCSS for styling.
- [ ] In `app/api.py`, configure FastAPI's `StaticFiles` to serve the built React app.

### Task 4.2: UI Implementation
- [ ] Create a `PartCard` React component to display the item's image, Hebrew name, explanation, price, and a link to the eBay listing.
- [ ] Create a `PartGrid` component that fetches data from `/v1/parts` on load and displays the cards in a grid.
- [ ] Add a simple loading indicator.
- [ ] Add a visual badge to cards if the `data_age_seconds` value indicates the data is stale (> 24 hours).

---

## Phase 5: Testing

### Task 5.1: Unit Tests
- [ ] **Scraper**: In `tests/test_scraper.py`, test the parsing logic using a static, saved HTML file from `tests/fixtures/` to avoid live network calls.
- [ ] **API**: In `tests/test_api.py`, use FastAPI's `TestClient` to test the API endpoints.
    - [ ] Test the `GET /v1/parts` endpoint for a successful response, and correct usage of `limit` and `query` parameters.
    - [ ] Test the `GET /v1/parts/{part_id}` endpoint for both successful and 404 responses.
    - [ ] Mock the `crud.py` functions to isolate the API layer for testing.

### Task 5.2: Integration Test
- [ ] Create an end-to-end test script (`tests/test_integration.py`) that:
    1. Sets up a temporary, in-memory SQLite database.
    2. Runs the scraper against a mock eBay server (e.g., using `pytest-httpx`).
    3. Verifies that data is correctly written to the test database.
    4. Queries the running test API to ensure the full flow works as expected.

---

## Phase 6: Deployment & Automation

### Task 6.1: Deployment Configuration
- [ ] Create a `render.yaml` file or document the manual steps for deploying to Render.
- [ ] Define the **Web Service**:
    - Start command: `uvicorn app.api:app --port $PORT --host 0.0.0.0`
- [ ] Define the **Background Worker** (Cron Job):
    - Start command: `python -m app.scraper`
    - Schedule: `0 */4 * * *` (every 4 hours).
- [ ] Ensure `requirements.txt` is up-to-date.

### Task 6.2: Validation
- [ ] Write a `README.md` with local setup and deployment instructions.
- [ ] Deploy the application to Render.
- [ ] Manually trigger the scraper and verify logs.
- [ ] Access the frontend and confirm data is displayed correctly.
- [ ] Set up basic logging to track the validation metrics (API latency, click-throughs, etc.).
