import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file (explicit path)
env_path = os.path.join(os.path.dirname(__file__), "src", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loading .env from: {env_path}")
else:
    load_dotenv()
    print("Loading .env from default location")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY loaded: {bool(GEMINI_API_KEY)}")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        print("Listing models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("No API Key found.")
