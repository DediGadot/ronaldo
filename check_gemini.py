import os
import google.generativeai as genai

try:
    # Configure the Gemini API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
    else:
        genai.configure(api_key=api_key)
        print("Available Gemini Models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"- {model.name}")
except Exception as e:
    print(f"An error occurred while checking Gemini models: {e}")
