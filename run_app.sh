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
        --help)
            echo "Usage: $0 [backend_port] [frontend_port] [options]"
            echo ""
            echo "Options:"
            echo "  --recreate-db    Delete and recreate the database from scratch"
            echo "  --run-scrapers   Run scrapers to populate the database with Ronaldo items"
            echo "  --aliexpress-only Run only AliExpress spider (works with --run-scrapers)"
            echo "  --ebay-only      Run only eBay spider (works with --run-scrapers)"
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

echo "Attempting to stop any running application processes..."

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
    if [ "$ALIEXPRESS_ONLY" = true ]; then
        echo "🕷️  Running AliExpress spider for Ronaldo items..."
        echo "  Scraping Ronaldo merchandise from AliExpress..."
        scrapy crawl aliexpress -s CLOSESPIDER_ITEMCOUNT=20 >/dev/null 2>&1 || echo "  ⚠️  AliExpress spider failed"
        echo "✅ AliExpress scraper completed"
    elif [ "$EBAY_ONLY" = true ]; then
        echo "🕷️  Running eBay spider for Ronaldo items..."
        echo "  Scraping Ronaldo collectibles from eBay..."
        scrapy crawl ebay -s CLOSESPIDER_ITEMCOUNT=30 >/dev/null 2>&1 || echo "  ⚠️  eBay spider failed"
        echo "✅ eBay scraper completed"
    else
        echo "🕷️  Running all scrapers to populate database with Ronaldo items..."
        echo "  Scraping Ronaldo collectibles from eBay..."
        scrapy crawl ebay -s CLOSESPIDER_ITEMCOUNT=25 >/dev/null 2>&1 || echo "  ⚠️  eBay spider failed"
        echo "  Scraping Ronaldo merchandise from AliExpress..."
        scrapy crawl aliexpress -s CLOSESPIDER_ITEMCOUNT=15 >/dev/null 2>&1 || echo "  ⚠️  AliExpress spider failed"
        echo "✅ All scrapers completed"
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
echo "Usage: ./run_app.sh [backend_port] [frontend_port] [options]"
echo "Examples:"
echo "  ./run_app.sh                              # Default ports (8000, 5173)"
echo "  ./run_app.sh 8080                         # Custom backend port"
echo "  ./run_app.sh 8080 3000                    # Custom backend and frontend ports"
echo "  ./run_app.sh --recreate-db                # Recreate database with default ports"
echo "  ./run_app.sh 8080 3000 --recreate-db      # Custom ports and recreate database"
echo "  ./run_app.sh --recreate-db --run-scrapers # Recreate DB and run scrapers"
echo "  ./run_app.sh --aliexpress-only --run-scrapers # Run only AliExpress spider"
echo "  ./run_app.sh --ebay-only --run-scrapers   # Run only eBay spider"
echo "  ./run_app.sh --recreate-db --run-scrapers --aliexpress-only # Fresh DB with AliExpress only"
echo ""
echo "To stop the application, run the following command:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo ""
