import google.generativeai as genai
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not set")
    exit(1)

genai.configure(api_key=api_key)

print("Listing ALL available models:")
try:
    for m in genai.list_models():
        print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
