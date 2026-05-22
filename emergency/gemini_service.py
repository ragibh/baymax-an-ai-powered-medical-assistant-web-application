import logging
import random

import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# gemini-1.5-flash is retired; use models available on your API key
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash",
]

SYSTEM_INSTRUCTION = (
    "You are Blobax, a compassionate AI health assistant. "
    "Give clear, helpful health information. Always recommend "
    "consulting a real doctor for serious concerns. "
    "Keep answers concise and friendly."
)


def get_gemini_response(message: str, history: list = None) -> str:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return "⚠️ Gemini API key not configured. Add GEMINI_API_KEY to your .env file."
    genai.configure(api_key=api_key)
    chat_history = []
    if history:
        for h in history[-6:]:
            chat_history.append({"role": "user", "parts": [h["user"]]})
            chat_history.append({"role": "model", "parts": [h["bot"]]})

    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_INSTRUCTION,
            )
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(message)
            return response.text.strip()
        except Exception as e:
            last_error = e
            logger.warning("Gemini model %s failed: %s", model_name, e)
            err = str(e).lower()
            if "404" not in err and "not found" not in err:
                break

    logger.error("Gemini error: %s", last_error)
    err_text = str(last_error or "").lower()
    if "429" in err_text or "quota" in err_text:
        return (
            "⚠️ Gemini API quota exceeded. Wait a few minutes or check billing at "
            "https://aistudio.google.com/apikey — then try again."
        )
    if "api key" in err_text or "invalid" in err_text:
        return "⚠️ Invalid GEMINI_API_KEY in .env. Create a new key at Google AI Studio."
    return "I'm having trouble connecting right now. Please try again in a moment."


class GeminiService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        self.setup_complete = bool(self.api_key)
        self.model_name = GEMINI_MODELS[0] if self.setup_complete else None

    def chat(self, user_message, conversation_history=None):
        history = None
        if conversation_history:
            history = []
            for item in conversation_history:
                if isinstance(item, dict) and "user" in item:
                    history.append(item)
        return get_gemini_response(user_message, history=history)

    def reset_conversation(self):
        pass


gemini_service = GeminiService()
