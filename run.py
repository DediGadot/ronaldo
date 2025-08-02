#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
import time

# Parse command line arguments
PORT = "8000"
FRONTEND_PORT = "5173"
SOURCE = "all"  # default to all sources

# Check for port argument
if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
    PORT = sys.argv[1]

# Check for source argument
if "--aliexpress-only" in sys.argv:
    SOURCE = "aliexpress"
elif "--ebay-only" in sys.argv:
    SOURCE = "ebay"
elif "--schmiedmann-only" in sys.argv:
    SOURCE = "schmiedmann"

# Check for frontend port argument
for i, arg in enumerate(sys.argv):
    if arg == "--frontend-port" and i + 1 < len(sys.argv):
        FRONTEND_PORT = sys.argv[i + 1]

print(f"🚀 Starting BMW E28 Parts Scraper")
print(f"Backend Port: {PORT}")
print(f"Frontend Port: {FRONTEND_PORT}")
print(f"Source: {SOURCE}")

# Kill existing processes on the target ports
def kill_processes_on_port(port):
    try:
        result = subprocess.run(["lsof", "-t", "-i:" + port], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    subprocess.run(["kill", "-9", pid], check=True)
                    print(f"✅ Killed process {pid} on port {port}")
                except subprocess.CalledProcessError:
                    pass
    except FileNotFoundError:
        # lsof not available, skip
        pass

kill_processes_on_port(PORT)
kill_processes_on_port(FRONTEND_PORT)

try:
    print("📡 Starting FastAPI backend...")
    backend = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", PORT],
        stdout=open("backend.log", "w"),
        stderr=subprocess.STDOUT
    )
    
    # Give backend time to start
    time.sleep(2)
    
    print(f"🕷️ Running scrapers for {SOURCE} source(s)...")
    scraped_any = False
    
    if SOURCE == "all" or SOURCE == "ebay":
        print("  Running eBay spider...")
        result = subprocess.run(["scrapy", "crawl", "ebay"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ eBay spider completed successfully")
            scraped_any = True
        else:
            print(f"  ❌ eBay spider failed: {result.stderr[-200:]}")
    
    if SOURCE == "all" or SOURCE == "aliexpress":
        print("  Running AliExpress spider...")
        result = subprocess.run(["scrapy", "crawl", "aliexpress"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ AliExpress spider completed successfully")
            scraped_any = True
        else:
            print(f"  ❌ AliExpress spider failed: {result.stderr[-200:]}")
    
    if SOURCE == "all" or SOURCE == "schmiedmann":
        print("  Running Schmiedmann E28 spider...")
        result = subprocess.run(["scrapy", "crawl", "schmiedmann_e28"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Schmiedmann E28 spider completed successfully")
            scraped_any = True
        else:
            print(f"  ❌ Schmiedmann E28 spider failed: {result.stderr[-200:]}")
        
        print("  Running Schmiedmann F10 spider...")
        result = subprocess.run(["scrapy", "crawl", "schmiedmann_f10"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Schmiedmann F10 spider completed successfully")
            scraped_any = True
        else:
            print(f"  ❌ Schmiedmann F10 spider failed: {result.stderr[-200:]}")
    
    # Always run the stories spider to populate engaging content
    print("  Running Ronaldo Stories spider...")
    result = subprocess.run(["scrapy", "crawl", "ronaldo_stories"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅ Ronaldo Stories spider completed successfully")
    else:
        print(f"  ⚠️ Ronaldo Stories spider warning: {result.stderr[-200:]}")
    
    # Populate default stories and generate AI content if Gemini is available
    print("  Setting up story content...")
    try:
        result = subprocess.run(["python", "-c", 
                               "from app.story_generator import populate_default_stories; populate_default_stories()"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Default stories populated successfully")
        else:
            print(f"  ⚠️ Story setup warning: {result.stderr[-200:]}")
    except Exception as e:
        print(f"  ⚠️ Story setup failed: {e}")
    
    if not scraped_any:
        print("⚠️ Warning: No scrapers completed successfully")
    
    # Try to start frontend if it exists
    frontend = None
    if os.path.exists("frontend") and os.path.exists("frontend/package.json"):
        print("🎨 Starting frontend...")
        try:
            frontend = subprocess.Popen(
                ["npm", "run", "dev", "--", "--host", "--port", FRONTEND_PORT],
                cwd="frontend",
                stdout=open("frontend.log", "w"),
                stderr=subprocess.STDOUT
            )
            print("  ✅ Frontend started successfully")
        except FileNotFoundError:
            print("  ⚠️ npm not found, skipping frontend")
        except Exception as e:
            print(f"  ⚠️ Frontend failed to start: {e}")
    else:
        print("  ℹ️ No frontend directory found, running backend only")
    
    print(f"\n🎯 Application Status:")
    print(f"  Backend PID: {backend.pid}")
    if frontend:
        print(f"  Frontend PID: {frontend.pid}")
    
    print(f"\n🌐 Access URLs:")
    print(f"  Backend API: http://localhost:{PORT}")
    if frontend:
        print(f"  Frontend: http://localhost:{FRONTEND_PORT}")
    
    print(f"\n📊 API Endpoints:")
    print(f"  All parts: curl http://localhost:{PORT}/api/parts/")
    if SOURCE == "all":
        print(f"  eBay only: curl 'http://localhost:{PORT}/api/parts/?source=eBay'")
        print(f"  AliExpress only: curl 'http://localhost:{PORT}/api/parts/?source=AliExpress'")
        print(f"  Schmiedmann only: curl 'http://localhost:{PORT}/api/parts/?source=Schmiedmann'")
    elif SOURCE == "aliexpress":
        print(f"  AliExpress parts: curl http://localhost:{PORT}/api/parts/")
        print("  (Running with AliExpress parts only)")
    elif SOURCE == "ebay":
        print(f"  eBay parts: curl http://localhost:{PORT}/api/parts/")
        print("  (Running with eBay parts only)")
    elif SOURCE == "schmiedmann":
        print(f"  Schmiedmann parts: curl http://localhost:{PORT}/api/parts/")
        print("  (Running with Schmiedmann parts only)")
    
    print(f"\n📝 Logs:")
    print(f"  Backend: tail -f backend.log")
    if frontend:
        print(f"  Frontend: tail -f frontend.log")
    
    print(f"\n🛠️ Usage:")
    print("  python run.py                                       # Run with all sources (default)")
    print("  python run.py 8080                                  # Run on custom backend port with all sources")
    print("  python run.py --aliexpress-only                     # Run with only AliExpress items")
    print("  python run.py --ebay-only                           # Run with only eBay items")
    print("  python run.py --schmiedmann-only                    # Run with only Schmiedmann items")
    print("  python run.py 8080 --schmiedmann-only               # Run on custom backend port with only Schmiedmann items")
    print("  python run.py --frontend-port 3000                  # Run with custom frontend port")
    print("  python run.py 8080 --frontend-port 3000 --ebay-only # Run with custom backend and frontend ports")
    
    print(f"\n⏳ Press Ctrl+C to stop...")
    
    # Wait for interrupt
    try:
        signal.pause()
    except AttributeError:
        # Windows doesn't have signal.pause(), use a different approach
        while True:
            time.sleep(1)
            
except KeyboardInterrupt:
    print("\n🛑 Shutting down...")
    try:
        backend.terminate()
        print("  ✅ Backend stopped")
    except:
        pass
    
    if frontend:
        try:
            frontend.terminate()
            print("  ✅ Frontend stopped")
        except:
            pass
    
    print("👋 Goodbye!")