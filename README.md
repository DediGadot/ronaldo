# 🐐 Cristiano Ronaldo Collectibles Hub

This project is a comprehensive web application designed to discover, catalog, and display authentic Cristiano Ronaldo memorabilia, jerseys, and collectibles from multiple sources across the internet. Built with AI-powered descriptions and modern search capabilities to help fans and collectors find genuine Ronaldo items from every era of his legendary career.

## Features

- **🔍 Multi-Source Discovery:** Advanced Scrapy spiders search eBay, AliExpress, and specialty sports retailers for authentic Ronaldo items
- **⚽ Career Era Filtering:** Browse items by Ronaldo's legendary career periods - Sporting, United, Madrid, Juventus, Portugal, Al-Nassr
- **🏆 Category Organization:** Organize by item types - jerseys, boots, memorabilia, signed items, trading cards, and collectibles
- **🤖 AI-Powered Descriptions:** Gemini AI generates detailed descriptions highlighting each item's significance in Ronaldo's career
- **💎 Authenticity Tracking:** Track item condition, authenticity status, and certificate of authenticity (COA) information
- **🎨 Modern Football UI:** React-based interface with Ronaldo-themed golden colors, responsive design, and infinite scroll
- **📊 Smart Filtering:** Filter by era, category, team, size, condition, and source with intelligent result mixing
- **🔗 Direct Purchase Links:** Quick access to original listings on eBay, AliExpress, and other marketplaces
- **📱 Mobile Optimized:** Fully responsive design optimized for collectors on mobile devices
- **🚀 Production Ready:** Docker support, comprehensive testing, and robust error handling with demo data fallbacks

## Tech Stack

- **Backend:**
  - **Framework:** FastAPI with CORS and advanced routing
  - **Database:** SQLite with SQLAlchemy ORM supporting both legacy parts and new Ronaldo items
  - **Web Scraping:** Scrapy 2.13+ with intelligent search queries for Ronaldo memorabilia
  - **AI Content Generation:** Google Gemini API for football-specific Hebrew/English descriptions
  - **Data Processing:** Smart categorization by career era, item type, and authenticity status
  - **Pipeline Processing:** Multi-source validation with football item enrichment

- **Frontend:**
  - **Framework:** React 18+ with Vite for fast development
  - **Styling:** Modern CSS with Ronaldo-themed golden gradients and football aesthetics
  - **UI Components:** Dynamic item cards with career era badges, team labels, and condition indicators
  - **User Experience:** Infinite scroll, era/category filtering, and source selection with football-focused design

## Project Structure

```
/
├── app/                       # Main backend application folder
│   ├── api.py                 # FastAPI endpoints with advanced source filtering
│   ├── crud.py                # Database operations with multi-source support
│   ├── database.py            # SQLAlchemy setup with optimized queries
│   ├── main.py                # FastAPI entrypoint with CORS configuration
│   ├── models.py              # Database models with source and series support
│   ├── schemas.py             # Pydantic schemas for API validation
│   ├── utils.py               # Utility functions for intelligent result shuffling
│   ├── pipelines.py           # Multi-source scraper pipeline with validation
│   ├── settings.py            # Scrapy settings with Playwright integration
│   └── spiders/               # Production-ready scrapy spiders
│       ├── ebay_spider.py           # eBay scraper with anti-detection
│       ├── aliexpress_spider.py     # AliExpress scraper with demo fallbacks
│       ├── schmiedmann_spider.py    # 🆕 Schmiedmann scraper with Playwright
│       ├── fcpeuro_spider.py        # FCP Euro scraper (placeholder)
│       ├── rockauto_spider.py       # RockAuto scraper (placeholder)
│       └── spareto_spider.py        # Spareto scraper (placeholder)
├── frontend/                  # React frontend with modern UI
│   ├── src/
│   │   ├── components/
│   │   │   └── PartCard.jsx   # Enhanced part cards with source badges
│   │   ├── App.jsx            # Main app with infinite scroll
│   │   └── App.css            # Responsive CSS with source-specific styling
│   └── vite.config.js
├── static/                    # Built frontend assets served by FastAPI
├── tests/                     # Comprehensive test suite (25+ tests)
│   ├── test_aliexpress_spider.py     # AliExpress spider tests (9 tests)
│   ├── test_schmiedmann_spider.py    # 🆕 Schmiedmann spider tests (19 tests)
│   ├── test_schmiedmann_integration.py # 🆕 Integration tests
│   ├── test_api_source_filtering.py  # API filtering tests
│   ├── test_utils.py                 # Utility function tests
│   └── test_api.py                   # General API tests
├── schmi.md                   # 🆕 Schmiedmann implementation documentation
├── Dockerfile                 # Production containerization
├── prompts.yaml               # Gemini AI prompt configuration
├── requirements.txt           # Python dependencies (updated with Playwright)
├── run.py                     # Enhanced application runner with source options
├── check_db.py                # Database inspection utility
└── update_descriptions.py     # AI-powered description enrichment
```

## Setup and Installation

Follow these steps to set up the project on your local machine.

### 1. Prerequisites

- **Python 3.10+** with pip package manager
- **Node.js 20.x+** and npm for frontend development
- **Playwright browsers**: Chromium will be installed automatically
- **Environment Variables:**
  - `GEMINI_API_KEY` - Required for AI-powered Hebrew descriptions
  - `SERPAPI_KEY` - Optional for enhanced part descriptions and search enrichment

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd e28
    ```

2.  **Set up the Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers:**
    ```bash
    playwright install chromium
    ```

5.  **Install frontend dependencies:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

## Database Management

The application uses a SQLite database (`ronaldo_items.db`) with multi-source support for Ronaldo collectibles.

### Database Schema

The database supports both legacy BMW parts and the new Ronaldo items structure:

**Ronaldo Items (Primary):**
- **eBay**: Ronaldo memorabilia from eBay auctions and buy-it-now listings
- **AliExpress**: Ronaldo merchandise from AliExpress marketplace with demo data fallbacks
- **Sports Retailers**: Authentic items from specialized sports memorabilia dealers

**Enhanced Schema Features:**
- **Career Era Categorization:** Sporting, United, Madrid, Juventus, Portugal, Al-Nassr periods
- **Item Categories:** Jerseys, boots, memorabilia, signed items, trading cards, collectibles
- **Authenticity Tracking:** Condition, authenticity status, COA information
- **Team & Year Details:** Specific team associations and season/year information
- **Size Information:** Clothing sizes for jerseys and boots
- **Bilingual Descriptions:** Football-focused English/Hebrew descriptions via AI
- **Multi-source Support:** Intelligent deduplication across all sources

### Database Utilities

- **Check Database Contents:**
  ```bash
  python check_db.py
  ```
  Displays database statistics including part counts by source and series.

### How to Populate the Database

The database is automatically created when the application starts. To populate it with data:

1.  **Run Individual Spiders:**
    ```bash
    # Scrape Ronaldo items from eBay
    scrapy crawl ebay
    
    # Scrape Ronaldo merchandise from AliExpress
    scrapy crawl aliexpress
    
    # List all available spiders
    scrapy list
    
    # List all available spiders
    scrapy list
    
    # Run with item limits for testing
    scrapy crawl schmiedmann_e28 -s CLOSESPIDER_ITEMCOUNT=5
    ```

2.  **Enrich Descriptions with AI:**
    ```bash
    python update_descriptions.py
    ```
    Uses the Gemini API to generate detailed Hebrew descriptions for all parts.

## Running the Application

### Quick Start

The main application runner provides several options for different use cases:

```bash
# Run with all sources (default)
python run.py

# Run on custom port with all sources
python run.py 8080

# Run with only AliExpress items
python run.py --aliexpress-only

# Run with only eBay items  
python run.py --ebay-only

# 🆕 Run with only Schmiedmann items
python run.py --schmiedmann-only

# Run on custom port with specific source
python run.py 8080 --schmiedmann-only

# Run with custom frontend port
python run.py --frontend-port 3000

# Run with custom backend and frontend ports
python run.py 8080 --frontend-port 3000 --schmiedmann-only
```

### Application Components

The runner automatically:
1. **Starts the FastAPI backend** on the specified port (default: 8000)
2. **Runs the selected scrapers** to populate the database
3. **Starts the frontend development server** on port 5173 (if frontend exists)

### Manual Component Management

#### Backend Only
```bash
# Start just the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start with auto-reload for development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Individual Scrapers
```bash
# List all available spiders
scrapy list

# Run specific spiders
scrapy crawl ebay
scrapy crawl aliexpress
scrapy crawl schmiedmann_e28      # 🆕 Schmiedmann E28 parts
scrapy crawl schmiedmann_f10      # 🆕 Schmiedmann F10 parts
scrapy crawl fcpeuro
scrapy crawl rockauto
scrapy crawl spareto

# Run with item limit for testing
scrapy crawl aliexpress -s CLOSESPIDER_ITEMCOUNT=10
scrapy crawl schmiedmann_e28 -s CLOSESPIDER_ITEMCOUNT=5
```

#### Frontend Development (if available)
```bash
cd frontend
npm run dev
```

#### Alternative Script Runner
```bash
# Run with default ports (backend: 8000, frontend: 5173)
./run_app.sh

# Run with custom backend port, default frontend port
./run_app.sh 8080

# Run with custom backend and frontend ports
./run_app.sh 8080 3000

# Recreate database from scratch and run with default ports
./run_app.sh --recreate-db

# Recreate database and populate with fresh data from scrapers
./run_app.sh --recreate-db --run-scrapers

# Custom ports with database recreation and scraper run
./run_app.sh 8080 3000 --recreate-db --run-scrapers

# Run only AliExpress spider to populate database
./run_app.sh --aliexpress-only --run-scrapers

# Fresh database with only AliExpress data
./run_app.sh --recreate-db --run-scrapers --aliexpress-only

# Show help for all options
./run_app.sh --help
```

### API Endpoints

Once running, the API provides these endpoints:

#### Get All Parts
```bash
curl "http://localhost:8000/api/parts/"
```

#### Filter by Source
```bash
# Get only eBay parts
curl "http://localhost:8000/api/parts/?source=eBay"

# Get only AliExpress parts
curl "http://localhost:8000/api/parts/?source=AliExpress"

# 🆕 Get only Schmiedmann parts
curl "http://localhost:8000/api/parts/?source=Schmiedmann"
```

#### Filter by Series
```bash
# Get only E28 parts
curl "http://localhost:8000/api/parts/?series=E28"

# Get only F10 parts
curl "http://localhost:8000/api/parts/?series=F10"
```

#### Combined Filtering
```bash
# Get E28 parts from AliExpress only
curl "http://localhost:8000/api/parts/?series=E28&source=AliExpress"

# 🆕 Get F10 parts from Schmiedmann only
curl "http://localhost:8000/api/parts/?series=F10&source=Schmiedmann"
```

#### Pagination
```bash
# Skip first 10, limit to 5 results
curl "http://localhost:8000/api/parts/?skip=10&limit=5"
```

#### Get Individual Part
```bash
curl "http://localhost:8000/api/parts/1"
```

### Production (Docker)

A `Dockerfile` is included for building a containerized version of the application.

1.  **Build the Docker image:**
    ```bash
    docker build -t e28-app .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 8000:8000 -e GEMINI_API_KEY=$GEMINI_API_KEY -e SERPAPI_KEY=$SERPAPI_KEY e28-app
    ```

The application will be available at **http://localhost:8000**.

## Development Tools & Testing

### Running Tests

The project includes a comprehensive test suite with 25+ test cases covering spider functionality, API endpoints, and utility functions.

```bash
# Run all tests
python -m pytest

# Run specific test files
python -m pytest tests/test_aliexpress_spider.py -v          # 9 AliExpress tests
python -m pytest tests/test_schmiedmann_spider.py -v        # 🆕 19 Schmiedmann tests
python -m pytest tests/test_schmiedmann_integration.py -v   # 🆕 Integration tests
python -m pytest tests/test_api_source_filtering.py -v      # API filtering tests
python -m pytest tests/test_utils.py -v                     # Utility function tests

# Run tests with coverage report
python -m pytest --cov=app tests/ --cov-report=html

# Run only spider tests
python -m pytest tests/ -k "spider" -v

# Test specific spider functionality
python -m pytest tests/test_schmiedmann_spider.py::TestSchmiedmannSpider::test_parse_price_method -v
```

**Test Coverage:**
- **Spider Tests**: 28 tests covering parsing, price conversion, URL handling, demo data
- **Integration Tests**: API endpoints, database operations, source filtering
- **Utility Tests**: Result shuffling, data validation, error handling
- **Performance Tests**: Memory usage, crawl speed, data quality metrics

### Database Tools

#### Inspect Database Contents
```bash
# View database statistics and sample data
python check_db.py
```

#### Test Database Operations
```bash
# Test model creation and database operations
python test_models.py
```

#### Reset Database
```bash
# Remove database file to start fresh
rm -f e28_parts.db

# Database will be recreated automatically on next run
python run.py
```

### Spider Development & Testing

#### Test Individual Spider Logic
```bash
# Test spider parsing with mock data
python -c "
from scrapy.http import HtmlResponse
from app.spiders.aliexpress_spider import AliexpressSpider

spider = AliexpressSpider()
# Add your test HTML and run spider.parse()
"
```

#### Debug Spider Requests
```bash
# Run spider with verbose logging
scrapy crawl aliexpress -L DEBUG

# Save scraped items to file for inspection
scrapy crawl ebay -o items.json
```

#### Spider Settings Override
```bash
# Run with custom settings
scrapy crawl aliexpress -s DOWNLOAD_DELAY=5 -s CONCURRENT_REQUESTS=1
```

### API Development

#### Test API Endpoints Manually
```bash
# Test with different parameters
curl -v "http://localhost:8000/api/parts/"
curl -v "http://localhost:8000/api/parts/?source=eBay&series=E28&limit=5"

# Test JSON response format
curl -H "Accept: application/json" "http://localhost:8000/api/parts/" | jq '.'
```

#### Monitor API Performance
```bash
# Run with uvicorn logs
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

## Troubleshooting

### Common Issues

#### 1. Spider Not Finding Items
```bash
# Check robot.txt compliance
scrapy view "https://www.aliexpress.com/robots.txt"
scrapy view "https://www.schmiedmann.com/robots.txt"

# Test with different user agent
scrapy crawl aliexpress -s USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Reduce request rate to avoid blocking  
scrapy crawl aliexpress -s DOWNLOAD_DELAY=10
scrapy crawl schmiedmann_e28 -s DOWNLOAD_DELAY=8

# 🆕 Debug Playwright issues
scrapy crawl schmiedmann_e28 -L DEBUG
```

#### 2. Database Connection Issues
```bash
# Check database file permissions
ls -la e28_parts.db

# Recreate database schema
rm e28_parts.db
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(engine)"
```

#### 3. Port Already in Use
```bash
# Find processes using port 8000
lsof -ti:8000

# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9

# Run on different port
python run.py 8001
```

#### 4. Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Install specific packages
pip install scrapy fastapi uvicorn sqlalchemy

# 🆕 Reinstall Playwright dependencies
pip install scrapy-playwright playwright
playwright install chromium
```

### Debugging Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug environment variables
export DEBUG=1
export PYTHONPATH=$PWD

# Run with verbose logging
python run.py --debug
```

### Performance Monitoring

#### Check Database Size
```bash
du -h e28_parts.db
sqlite3 e28_parts.db "SELECT COUNT(*) as total_parts FROM parts;"
```

#### Monitor Memory Usage
```bash
# Run with memory monitoring
scrapy crawl ebay -s MEMUSAGE_ENABLED=True
```

## Advanced Configuration

### Custom Spider Settings

Create custom settings for different environments:

```python
# In scrapy.cfg or spider files
[settings]
default = app.settings

[deploy:production]  
settings = app.settings_production
```

### 🆕 Playwright Configuration

For production deployment with Schmiedmann spider:

```python
# Enhanced Playwright settings in spider
custom_settings = {
    'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
    'PLAYWRIGHT_LAUNCH_OPTIONS': {
        'headless': True,
        'args': ['--no-sandbox', '--disable-dev-shm-usage']
    },
    'DOWNLOAD_DELAY': 5,
    'CONCURRENT_REQUESTS': 1,
}
```

### API Configuration

Environment variables for API customization:

```bash
# Set custom database URL
export DATABASE_URL="sqlite:///custom_path.db"

# Enable CORS for frontend development
export ENABLE_CORS=true

# Set custom API prefix
export API_PREFIX="/api/v1"
```

### Multi-Environment Setup

```bash
# Development environment
cp .env.example .env.dev
export ENV=development

# Production environment  
cp .env.example .env.prod
export ENV=production
```

## Contributing

### Code Quality

```bash
# Run linting
flake8 app/ tests/

# Format code
black app/ tests/

# Type checking (if using mypy)
mypy app/
```

### Adding New Spiders

1. **Create spider file** in `app/spiders/your_spider.py`
2. **Implement base methods**: `start_requests()`, `parse()`
3. **Add source identification**: `yield {"source": "YourSource", ...}`
4. **Configure anti-detection**: User-Agent rotation, delays, headers
5. **Handle JavaScript sites**: Use Playwright if needed (see `schmiedmann_spider.py`)
6. **Create comprehensive tests** in `tests/test_your_spider.py`
7. **Add demo data fallbacks** for when site blocks requests
8. **Update run.py** with new spider options
9. **Document implementation** and update README.md

**Example Spider Structure:**
```python
class YourSpider(scrapy.Spider):
    name = "your_spider"
    
    def start_requests(self):
        # Generate requests for your site
        pass
    
    def parse(self, response):
        # Extract and yield items with source field
        yield {"source": "YourSource", ...}
```

### Running Full Test Suite

```bash
# Comprehensive test suite with coverage
python -m pytest tests/ -v --cov=app --cov-report=html

# Quick test to verify all spiders work
python -c "
from app.spiders.ebay_spider import EbaySpider
from app.spiders.aliexpress_spider import AliexpressSpider  
from app.spiders.schmiedmann_spider import SchmiedmannE28Spider, SchmiedmannF10Spider
print('✅ All spiders imported successfully')
"
```

## 🆕 New in This Version

### Schmiedmann Integration
- **Complete Schmiedmann.com scraper** with Playwright support for JavaScript-heavy pages
- **EUR to USD conversion** with configurable exchange rates (current: 1.08)
- **Dual spider architecture**: Separate E28 and F10 spiders for targeted scraping
- **19 comprehensive unit tests** covering all functionality including price parsing and demo data
- **Production-ready features**: Anti-detection, error handling, demo data fallbacks

### Enhanced Architecture  
- **Multi-source pipeline** supporting unlimited number of parts sources
- **Frontend enhancements** with source-specific badges and styling
- **Advanced API filtering** by source, series, and combined parameters
- **Comprehensive testing** with 25+ test cases across all components
- **Production monitoring** with detailed logging and performance metrics

### Developer Experience
- **Updated documentation** with complete setup and troubleshooting guides
- **Enhanced debugging tools** for spider development and testing
- **Playwright integration** for modern web scraping capabilities
- **Demo data system** ensuring application works even when sites block requests
