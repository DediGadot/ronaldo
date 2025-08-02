#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Parse command line arguments
PORT="8000"
FRONTEND_PORT="5173"
RECREATE_DB=false
RUN_SCRAPERS=false
ALIEXPRESS_ONLY=false
EBAY_ONLY=false
SCHMIEDMANN_ONLY=false
RUN_STORIES=true
KILL_ALL=false

# Process arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --recreate-db)
            RECREATE_DB=true
            shift
            ;;
        --run-scrapers)
            RUN_SCRAPERS=true
            shift
            ;;
        --aliexpress-only)
            ALIEXPRESS_ONLY=true
            shift
            ;;
        --ebay-only)
            EBAY_ONLY=true
            shift
            ;;
        --schmiedmann-only)
            SCHMIEDMANN_ONLY=true
            shift
            ;;
        --no-stories)
            RUN_STORIES=false
            shift
            ;;
        --kill-all)
            KILL_ALL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [backend_port] [frontend_port] [options]"
            echo ""
            echo "Options:"
            echo "  --recreate-db    Delete and recreate the database from scratch"
            echo "  --run-scrapers   Run scrapers to populate the database with Ronaldo items"
            echo "  --aliexpress-only Run only AliExpress spider (works with --run-scrapers)"
            echo "  --ebay-only      Run only eBay spider (works with --run-scrapers)"
            echo "  --schmiedmann-only Run only Schmiedmann spiders (works with --run-scrapers)"
            echo "  --no-stories     Skip story scraping and content generation"
            echo "  --kill-all       Kill all similar backend/frontend processes before starting"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Default ports (8000, 5173)"
            echo "  $0 8080                         # Custom backend port"
            echo "  $0 8080 3000                    # Custom backend and frontend ports"
            echo "  $0 --recreate-db                # Recreate database with default ports"
            echo "  $0 8080 3000 --recreate-db      # Custom ports and recreate database"
            echo "  $0 --recreate-db --run-scrapers # Recreate DB and run scrapers"
            echo "  $0 --aliexpress-only --run-scrapers # Run only AliExpress spider"
            echo "  $0 --ebay-only --run-scrapers   # Run only eBay spider"
            echo "  $0 --schmiedmann-only --run-scrapers # Run only Schmiedmann spiders"
            echo "  $0 --no-stories --run-scrapers  # Run scrapers without story content"
            echo "  $0 --recreate-db --run-scrapers --aliexpress-only # Fresh DB with AliExpress only"
            exit 0
            ;;
        [0-9]*)
            if [ "$PORT" = "8000" ]; then
                PORT="$1"
            elif [ "$FRONTEND_PORT" = "5173" ]; then
                FRONTEND_PORT="$1"
            fi
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Handle database recreation if requested
if [ "$RECREATE_DB" = true ]; then
    echo "🗑️  Recreating database from scratch..."
    rm -f ronaldo_items.db e28_parts.db
    echo "✅ Database deleted successfully"
fi

# Kill all similar processes if requested
if [ "$KILL_ALL" = true ]; then
    echo "🔥 Killing all similar backend and frontend processes..."
    
    # Kill FastAPI/uvicorn processes
    echo "  Stopping FastAPI/uvicorn processes..."
    pkill -f "uvicorn" || true
    pkill -f "fastapi" || true
    
    # Kill Vite/npm development servers
    echo "  Stopping Vite/npm development servers..."
    pkill -f "vite" || true
    pkill -f "npm run dev" || true
    
    # Kill any Python processes running main.py or app
    echo "  Stopping Python app processes..."
    pkill -f "python.*main.py" || true
    pkill -f "python.*app" || true
    
    # Kill any node processes on common dev ports
    echo "  Stopping processes on common dev ports..."
    for port in 3000 5173 8000 8080; do
        pid=$(lsof -t -i:$port || true)
        if [ -n "$pid" ]; then
            echo "    Killing process on port $port (PID: $pid)"
            kill -9 $pid || true
        fi
    done
    
    echo "✅ All similar processes killed"
    sleep 2
fi

echo "Attempting to stop any running application processes on specified ports..."

# Find and kill the process using the specified backend port
BACKEND_PID=$(lsof -t -i:$PORT || true)
if [ -n "$BACKEND_PID" ]; then
  echo "Killing backend process on port $PORT with PID: $BACKEND_PID"
  kill -9 $BACKEND_PID || true
fi

# Find and kill the process using the specified frontend port
FRONTEND_PID=$(lsof -t -i:$FRONTEND_PORT || true)
if [ -n "$FRONTEND_PID" ]; then
  echo "Killing frontend process on port $FRONTEND_PORT with PID: $FRONTEND_PID"
  kill -9 $FRONTEND_PID || true
fi

echo "Starting FastAPI backend server on port $PORT..."
# Activate virtual environment and start the backend, redirecting output to backend.log
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port $PORT > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID. Log: backend.log"

# Run scrapers if requested
if [ "$RUN_SCRAPERS" = true ]; then
    echo "🕷️  Running scrapers to populate database with Ronaldo items..."
    
    if [ "$ALIEXPRESS_ONLY" = true ]; then
        echo "  Scraping Ronaldo merchandise from AliExpress..."
        scrapy crawl aliexpress -s CLOSESPIDER_ITEMCOUNT=25 >/dev/null 2>&1 || echo "  ⚠️  AliExpress spider failed"
        echo "✅ AliExpress scraper completed"
    elif [ "$EBAY_ONLY" = true ]; then
        echo "  Scraping Ronaldo collectibles from eBay..."
        scrapy crawl ebay -s CLOSESPIDER_ITEMCOUNT=30 >/dev/null 2>&1 || echo "  ⚠️  eBay spider failed"
        echo "✅ eBay scraper completed"
    elif [ "$SCHMIEDMANN_ONLY" = true ]; then
        echo "  Scraping BMW parts from Schmiedmann E28..."
        scrapy crawl schmiedmann_e28 -s CLOSESPIDER_ITEMCOUNT=20 >/dev/null 2>&1 || echo "  ⚠️  Schmiedmann E28 spider failed"
        echo "  Scraping BMW parts from Schmiedmann F10..."
        scrapy crawl schmiedmann_f10 -s CLOSESPIDER_ITEMCOUNT=20 >/dev/null 2>&1 || echo "  ⚠️  Schmiedmann F10 spider failed"
        echo "✅ Schmiedmann scrapers completed"
    else
        echo "  Scraping Ronaldo collectibles from eBay..."
        scrapy crawl ebay -s CLOSESPIDER_ITEMCOUNT=25 >/dev/null 2>&1 || echo "  ⚠️  eBay spider failed"
        echo "  Scraping Ronaldo merchandise from AliExpress..."
        scrapy crawl aliexpress -s CLOSESPIDER_ITEMCOUNT=20 >/dev/null 2>&1 || echo "  ⚠️  AliExpress spider failed"
        echo "  Scraping BMW parts from Schmiedmann E28..."
        scrapy crawl schmiedmann_e28 -s CLOSESPIDER_ITEMCOUNT=15 >/dev/null 2>&1 || echo "  ⚠️  Schmiedmann E28 spider failed"
        echo "  Scraping BMW parts from Schmiedmann F10..."
        scrapy crawl schmiedmann_f10 -s CLOSESPIDER_ITEMCOUNT=15 >/dev/null 2>&1 || echo "  ⚠️  Schmiedmann F10 spider failed"
        echo "✅ All item scrapers completed"
    fi
fi

# Run story content generation
if [ "$RUN_STORIES" = true ]; then
    echo "📚 Setting up Ronaldo story content..."
    
    # Run story spider
    echo "  Scraping Ronaldo stories and facts..."
    scrapy crawl ronaldo_stories -s CLOSESPIDER_ITEMCOUNT=20 >/dev/null 2>&1 || echo "  ⚠️  Stories spider failed (continuing anyway)"
    
    # Populate default stories
    echo "  Populating default story content..."
    python -c "from app.story_generator import populate_default_stories; populate_default_stories()" >/dev/null 2>&1 || echo "  ⚠️  Default story setup failed (continuing anyway)"
    
    # Generate contextual stories if Gemini API is available
    if [ -n "$GEMINI_API_KEY" ]; then
        echo "  Generating AI-powered contextual stories..."
        python -c "
from app.story_generator import generate_contextual_stories
for era in ['United', 'Madrid', 'Juventus', 'Portugal']:
    generate_contextual_stories(era=era, count=2)
print('AI story generation completed')
" >/dev/null 2>&1 || echo "  ⚠️  AI story generation failed (continuing anyway)"
        echo "✅ Story content setup completed with AI enhancement"
    else
        echo "✅ Story content setup completed (no GEMINI_API_KEY for AI enhancement)"
    fi
fi

echo "Starting Vite frontend development server on port $FRONTEND_PORT..."
# Navigate to the frontend directory and start the dev server, redirecting output to frontend.log
cd frontend
npm run dev -- --host --port $FRONTEND_PORT > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID. Log: ../frontend.log"
cd ..

echo ""
echo "🐐 Cristiano Ronaldo Collectibles Hub is running!"
echo "Backend API is available at http://localhost:$PORT"
echo "Frontend is available at http://localhost:$FRONTEND_PORT (and on your local network)"
echo ""
echo "🏆 New Features Available:"
echo "  • Football-themed UI with stadium atmosphere"
echo "  • Interactive story boxes with Ronaldo facts"
echo "  • Team-specific color schemes for different eras"
echo "  • Enhanced engagement features for casual fans"
echo "  • AI-powered contextual story generation"
echo ""
echo "📊 API Endpoints:"
echo "  • Items: GET /api/items/?era=Madrid&category=jerseys"
echo "  • Stories: GET /api/stories/?era=United&team=Manchester United"
echo "  • Generate Stories: POST /api/stories/generate"
echo ""
echo "Usage: ./run_app.sh [backend_port] [frontend_port] [options]"
echo "Examples:"
echo "  ./run_app.sh                              # Default ports with stories"
echo "  ./run_app.sh 8080                         # Custom backend port"
echo "  ./run_app.sh 8080 3000                    # Custom backend and frontend ports"
echo "  ./run_app.sh --recreate-db                # Fresh database with default stories"
echo "  ./run_app.sh --recreate-db --run-scrapers # Fresh DB with all content"
echo "  ./run_app.sh --aliexpress-only --run-scrapers # AliExpress items only"
echo "  ./run_app.sh --ebay-only --run-scrapers   # eBay collectibles only"
echo "  ./run_app.sh --schmiedmann-only --run-scrapers # BMW parts only"
echo "  ./run_app.sh --no-stories --run-scrapers  # Items without story content"
echo "  ./run_app.sh --kill-all                   # Kill all dev processes first"
echo "  ./run_app.sh --recreate-db --run-scrapers --aliexpress-only # Fresh AliExpress DB"
echo ""
echo "To stop the application, run the following command:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo ""
