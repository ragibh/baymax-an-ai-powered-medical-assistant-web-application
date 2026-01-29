import google.generativeai as genai

def test_gemini_simple():
    try:
        # Replace with your actual API key
        API_KEY = "AIzaSyBledfCR1vqUSIypiM4-gUkZDG2azVTiRo"  # ⚠️ PUT YOUR REAL KEY HERE
        
        print(f"Testing API key: {API_KEY[:10]}...")
        
        genai.configure(api_key=API_KEY)
        
        # List available models
        print("🔍 Checking available models...")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
        
        # Test the model
        print("\n🧪 Testing chat...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, say 'Baymax is working!' if you can read this.")
        print(f"Response: {response.text}")
        
        print("\n🎉 Gemini API is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_simple()