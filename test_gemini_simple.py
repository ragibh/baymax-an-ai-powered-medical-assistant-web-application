# save as debug_key.py
import google.generativeai as genai

KEY = ".."  # paste your new key directly here

genai.configure(api_key=KEY)

print("Testing key:", KEY[:15], "...")

try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Say hello in one word")
    print("✅ SUCCESS:", response.text)
except Exception as e:
    print("❌ FAILED:", e)