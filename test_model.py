"""
Quick test script to check which Gemini models are available with your API key.
Run this to debug model availability issues.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("Testing Gemini API Connection")
print("=" * 60)

# List available models
print("\n1. Listing available models...")
try:
    models = genai.list_models()
    available = [m for m in models if 'generateContent' in m.supported_generation_methods]
    print(f"Found {len(available)} models that support generateContent:\n")
    for model in available[:10]:
        print(f"  - {model.name}")
        if hasattr(model, 'display_name'):
            print(f"    Display Name: {model.display_name}")
except Exception as e:
    print(f"ERROR listing models: {str(e)}")
    available = []

# Test common model names (with and without models/ prefix)
print("\n2. Testing common model names...")
test_models = [
    "models/gemini-2.5-flash",  # Latest
    "models/gemini-2.0-flash",   # Stable 2.0
    "models/gemini-2.0-flash-001",
    "models/gemini-2.0-flash-lite",
    "gemini-2.5-flash",  # Try without prefix
    "gemini-2.0-flash",
    "gemini-pro",  # Legacy
    "gemini-1.5-flash",  # Legacy
    "gemini-1.5-pro",  # Legacy
]

working_models = []
for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        # Try a simple generation to verify it works
        response = model.generate_content("Say 'test' if you can read this.")
        if response and hasattr(response, 'text'):
            print(f"  [OK] {model_name} - WORKS")
            working_models.append(model_name)
        else:
            print(f"  [?] {model_name} - Created but response issue")
    except Exception as e:
        print(f"  [X] {model_name} - FAILED: {str(e)[:80]}")

print("\n" + "=" * 60)
if working_models:
    print(f"SUCCESS: Found {len(working_models)} working model(s):")
    for m in working_models:
        print(f"  - {m}")
    print(f"\nRecommendation: Use GEMINI_MODEL={working_models[0]} in your .env file")
else:
    print("ERROR: No working models found!")
    print("Please check:")
    print("  1. Your API key is valid")
    print("  2. Your API key has access to Gemini models")
    print("  3. You're using the latest SDK: pip install --upgrade google-generativeai")
print("=" * 60)

