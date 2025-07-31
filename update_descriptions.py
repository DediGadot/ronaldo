import sys
import os
import yaml
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Part
import google.generativeai as genai
from serpapi import GoogleSearch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Load Configuration ---
try:
    with open("prompts.yaml", "r") as f:
        config = yaml.safe_load(f)
    GEMINI_MODEL_NAME = config["gemini_model"]
    PROMPT_TEMPLATE = config["generate_hebrew_description"]
except (FileNotFoundError, KeyError) as e:
    print(f"Error loading configuration from prompts.yaml: {e}")
    sys.exit(1)

# --- API Configuration ---
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    GEMINI_MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)
except KeyError:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)
except Exception as e:
    print(f"Error configuring Gemini with model {GEMINI_MODEL_NAME}: {e}")
    sys.exit(1)

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

# --- Functions ---

def get_search_snippet(query):
    """Gets the top search result snippet from SerpApi."""
    if not SERPAPI_KEY:
        print("  - SERPAPI_KEY not found. Using title as description fallback.")
        return query

    try:
        params = {"q": query, "engine": "google", "api_key": SERPAPI_KEY}
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "organic_results" in results and results["organic_results"]:
            return results["organic_results"][0].get("snippet", query)
        return query
    except Exception as e:
        print(f"  - SerpApi search failed: {e}")
        return query

def generate_hebrew_description(part_title, search_snippet):
    """Generates a Hebrew description using the Gemini API."""
    prompt = PROMPT_TEMPLATE.format(part_title=part_title, search_snippet=search_snippet)
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  - Gemini API call failed: {e}")
        return "תיאור מפורט אינו זמין כעת."

def update_descriptions():
    """Updates part descriptions in the database."""
    db = SessionLocal()
    try:
        parts_to_update = db.query(Part).all()
        if not parts_to_update:
            print("No parts found in the database.")
            return

        print(f"Found {len(parts_to_update)} parts to update.")

        for part in parts_to_update:
            print(f"Updating description for: {part.title_en}")

            # 1. Get search snippet
            snippet = get_search_snippet(part.title_en)

            # 2. Generate new Hebrew description
            enriched_he = generate_hebrew_description(part.title_en, snippet)

            # 3. Update the part in the database
            part.description_he = enriched_he
            part.description_en = part.title_en
            print("  - New Hebrew description generated.")

        db.commit()
        print("\nSuccessfully updated all part descriptions.")

    finally:
        db.close()

if __name__ == "__main__":
    update_descriptions()