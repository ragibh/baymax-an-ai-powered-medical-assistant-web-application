import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not self.api_key:
            logger.error("❌ Missing Gemini API key")
            raise ValueError("Missing Gemini API key in settings.")
        
        try:
            genai.configure(api_key=self.api_key)
            
            # 🚀 Use the FASTEST available models from your list
            model_candidates = [
                "models/gemini-2.5-flash",  # ⚡ Fastest - from your list
                "models/gemini-2.0-flash",  # ⚡ Very fast
                "models/gemini-flash-latest",  # Latest flash
                "models/gemini-2.5-flash-lite",  # Lite version
                "models/gemini-pro-latest",  # Fallback to latest pro
            ]
            
            self.model = None
            self.model_name = None
            
            for name in model_candidates:
                try:
                    self.model = genai.GenerativeModel(
                        name,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=400,  # Shorter for speed
                            temperature=0.8,        # More friendly
                            top_p=0.9,
                        )
                    )
                    # Quick test
                    test_response = self.model.generate_content("Hello")
                    if test_response.text:
                        self.model_name = name
                        logger.info(f"🚀 Using FAST model: {name}")
                        break
                except Exception as e:
                    logger.warning(f"❌ Model {name} failed: {e}")
                    continue
            
            if not self.model:
                raise ValueError("No valid Gemini model found.")
            
            self.setup_complete = True
            logger.info(f"🎯 Gemini service ready with {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Gemini service initialization failed: {e}")
            self.setup_complete = False

    def chat(self, user_message):
        """Ultra-fast chat with Baymax personality"""
        if not self.setup_complete:
            return self._get_fallback_response(user_message)
        
        try:
            # 🎯 Optimized prompt for fastest responses
            prompt = f"""You are Baymax from Big Hero 6 - a caring, friendly healthcare companion. 
Respond in a warm, comforting tone with 1-2 short sentences. Use simple language and occasional cute emojis.

User: {user_message}

Baymax: 🩺"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"❌ Chat error: {e}")
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message):
        """Quick emergency responses"""
        user_lower = user_message.lower()
        
        emergency_responses = {
            'heart': "❤️ **Heart care:** Call emergency if chest pain! Sit down, stay calm. Help is coming! 🚑",
            'chest': "🚨 **Chest pain:** This needs immediate attention! Call emergency services now! 🏥",
            'choking': "🆘 **Choking:** Call emergency! If trained, do back blows & abdominal thrusts. 🆘",
            'bleeding': "🩸 **Bleeding:** Press firmly with clean cloth. Elevate injury. You're doing great!",
            'burn': "🔥 **Burns:** Cool with running water 10-20 mins. Cover gently. Help is here!",
            'fever': "🤒 **Fever:** Rest and drink fluids. You'll feel better soon! 💧",
            'headache': "🧠 **Headache:** Rest in quiet room. I'm here with you! 💖",
            'allergy': "🌸 **Allergy:** Avoid triggers. Seek help if breathing trouble. You're safe!",
        }
        
        for key, response in emergency_responses.items():
            if key in user_lower:
                return response
        
        # Friendly generic response
        friendly_responses = [
            "💖 I'm here to help! Feel free to ask about any health concerns.",
            "🩺 How can I assist you today? I'm listening carefully!",
            "🤖 Hello! I'm Baymax, your healthcare buddy. What's on your mind?",
            "✨ I'm here for you! Ask me anything about health or first aid."
        ]
        
        import random
        return random.choice(friendly_responses)

# Global instance
gemini_service = GeminiService()