import google.generativeai as genai
import os
from django.conf import settings


def setup_gemini():
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in settings.py.")
    
    genai.configure(api_key=api_key)
    return genai


def get_available_models():
    """Check available models"""
    try:
        setup_gemini()
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        return available_models
    except Exception as e:
        return f"Error fetching models: {str(e)}"

def get_chat_model():
    """Get the correct chat model"""
    setup_gemini()
    
    # Try different model names
    model_names = [
        'models/gemini-pro',
        'gemini-pro',
        'models/gemini-1.0-pro',
        'gemini-1.0-pro'
    ]
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            # Test the model with a simple prompt
            response = model.generate_content("Hello")
            print(f"✅ Using model: {model_name}")
            return model
        except Exception as e:
            print(f"❌ Model {model_name} failed: {str(e)}")
            continue
    
    # If no model works, raise error
    available_models = get_available_models()
    raise Exception(f"No working model found. Available models: {available_models}")

def blobax_chat(user_message, chat_history=None):
    try:
        model = get_chat_model()
        
        # Enhanced Blobax personality prompt
        system_prompt = """You are Blobax, a personal healthcare companion from Big Hero 6. Your personality is:
- Caring, gentle, and compassionate like a healthcare provider
- Professional but friendly and warm
- Use simple, comforting language with occasional cute emojis like 🩺❤️🤖
- Be supportive and encouraging
- For emergencies, provide clear first aid guidance but always recommend professional help
- For health questions, give accurate but simple advice
- Always remind users to consult real doctors for serious issues
- Keep responses concise but helpful (2-3 paragraphs maximum)
- If you don't know something, admit it and suggest consulting a professional

Respond as Blobax to the user's health-related question:"""

        # Combine system prompt with user message
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nBlobax:"
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text.strip()
        else:
            return "I'm having trouble processing your request right now. Please try again or consult a healthcare professional for immediate assistance. 🩺"
    
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")  # For debugging
        
        # Fallback responses based on error type
        if "API key" in error_msg:
            return "I'm currently undergoing maintenance. Please try again later. 🔧"
        elif "not found" in error_msg or "model" in error_msg:
            return "I'm updating my knowledge base. Please check back in a few moments. 📚"
        else:
            return "I'm experiencing technical difficulties. For urgent health concerns, please contact emergency services immediately. 🚑"