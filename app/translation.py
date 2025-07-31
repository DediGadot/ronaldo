import yaml
from deep_translator import GoogleTranslator

def load_term_overrides():
    try:
        with open("terms.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

class PartTranslator:
    def __init__(self):
        self.overrides = load_term_overrides()

    def translate(self, text: str, dest_lang: str = "he") -> str:
        # Check for a direct override first
        if text.lower() in self.overrides:
            return self.overrides[text.lower()]

        # If no override, use deep-translator
        try:
            return GoogleTranslator(source='auto', target=dest_lang).translate(text)
        except Exception as e:
            print(f"Error translating '{text}': {e}")
            return text # Return original text on error