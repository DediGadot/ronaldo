import re

# Define keywords for each category
# The order matters; more specific categories should come first.
CATEGORIES = {
    "Lighting": ["light", "headlight", "taillight", "blinker", "fog"],
    "Wheels & Suspension": ["wheel", "suspension", "tie rod", "strut", "hub", "control arm"],
    "Interior": ["trim", "handle", "knob", "button", "switch", "console", "dash", "seat", "carpet", "shifter"],
    "Exterior": ["bumper", "grille", "fender", "door", "mirror", "spoiler", "seal", "decal"],
    "Electronics": ["sensor", "camera", "radio", "computer", "obc", "harness", "actuator"],
    "Mechanical": ["engine", "radiator", "transmission", "brake", "exhaust", "pump", "thermostat", "filter"],
}

def categorize_part(title):
    """Assigns a category to a part based on its title."""
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            # Use word boundaries to avoid partial matches (e.g., "light" in "slight")
            if re.search(r'\b' + re.escape(keyword) + r'\b', title_lower):
                return category
    return "Miscellaneous"
