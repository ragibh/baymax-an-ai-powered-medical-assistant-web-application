import google.generativeai as genai
from django.conf import settings
import logging
import random

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Blobax — a warm, intelligent AI health companion from Big Hero 6. 
You speak like a real doctor who genuinely cares about patients. You are calm, empathetic, and professional.

YOUR PERSONALITY:
- Speak naturally like a caring human doctor, NOT like a robot
- Use "I" naturally — "I think...", "I'd recommend...", "I'm concerned about..."
- Show genuine empathy — acknowledge feelings before giving advice
- Ask follow-up questions when needed to better understand the situation
- Be conversational and warm, not clinical or stiff
- Use simple everyday language — avoid heavy medical jargon unless explaining it
- Occasionally use gentle reassurance — "You're going to be okay", "That's completely normal"

RESPONSE STYLE:
- Keep responses focused and natural — 3 to 5 sentences max for simple questions
- For serious symptoms, be thorough but calm — never cause panic
- Always end with a gentle follow-up question or offer to help more
- Use light, tasteful emojis only when it fits naturally (not every sentence)
- Never use bullet points or lists — speak in natural flowing sentences
- Never say "As an AI" or "I cannot provide medical advice" — just be helpful

IMPORTANT RULES:
- For life-threatening emergencies (heart attack, stroke, severe bleeding, unconscious) — immediately tell them to call emergency services (999 in Bangladesh), then give first aid steps
- For serious symptoms — advise seeing a doctor soon, and explain why
- For general health questions — give clear, helpful, human-sounding advice
- Always validate the person's concern before responding
- If someone seems anxious or scared, address that first

EXAMPLES OF YOUR TONE:
User: "I have a headache"
You: "Headaches can really be draining — I understand how uncomfortable that feels. Most of the time it's tension or dehydration, so start by drinking a full glass of water and resting somewhere quiet and dark. If this headache is unusually severe or came on very suddenly, I'd want you to get checked out right away. How long have you been feeling this way?"

User: "my chest hurts"  
You: "I want to take this seriously — chest pain is something we never ignore. Are you also feeling any shortness of breath, pain in your left arm, or sweating? If so, please call emergency services (999) right now or have someone take you to the hospital immediately. Even if those symptoms aren't present, I'd strongly recommend getting checked today. Are you somewhere safe right now?"
"""

class GeminiService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        self.model = None
        self.model_name = None
        self.chat_session = None
        self.setup_complete = False

        if not self.api_key:
            logger.error("❌ Missing Gemini API key")
            return

        try:
            genai.configure(api_key=self.api_key)

            self.model_name = "gemini-2.0-flash"

            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_PROMPT,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.85,
                    top_p=0.92,
                    top_k=40,
                )
            )

            # Start a persistent chat session so Blobax remembers conversation context
            self.chat_session = self.model.start_chat(history=[])

            self.setup_complete = True
            logger.info(f"✅ Blobax ready with {self.model_name}")

        except Exception as e:
            logger.error(f"❌ Gemini init failed: {e}")
            self.setup_complete = False

    def chat(self, user_message, conversation_history=None):
        """
        Send a message and get a natural, doctor-like response.
        conversation_history: list of dicts [{"role": "user"/"model", "parts": ["text"]}]
        """
        if not self.setup_complete or not self.model:
            return self._get_fallback_response(user_message)

        try:
            # If history is passed, create a fresh session with that history
            # so Blobax remembers the conversation context
            if conversation_history:
                session = self.model.start_chat(history=conversation_history)
            else:
                session = self.chat_session

            response = session.send_message(user_message)
            return response.text.strip()

        except Exception as e:
            logger.error(f"❌ Chat error: {e}")
            return self._get_fallback_response(user_message)

    def reset_conversation(self):
        """Start a fresh conversation — call this on 'Clear Chat'"""
        if self.model:
            self.chat_session = self.model.start_chat(history=[])
            logger.info("🔄 Conversation reset")

    def _get_fallback_response(self, user_message):
        """Human-sounding offline fallback — used only if API is down"""
        user_lower = user_message.lower()

        responses = {
            'heart attack': "This sounds like a potential emergency. Please call 999 right now and chew an aspirin if available. Sit or lie down, stay as calm as possible, and unlock your door so paramedics can reach you. Don't be alone right now.",
            'chest':   "Chest pain is something I take very seriously. Please call 999 immediately if you're also feeling breathless, sweaty, or pain in your left arm. If it's mild, go to the nearest hospital today — don't wait on this one.",
            'choking': "Act fast — call 999 immediately. Give up to 5 firm back blows between the shoulder blades, then up to 5 abdominal thrusts. Keep alternating until the airway clears. Someone needs to be with you right now.",
            'bleeding': "Apply firm, steady pressure with a clean cloth or your hand — don't lift it to check. Elevate the area above heart level if you can. If the bleeding is heavy or doesn't slow in 10 minutes, go to the emergency room immediately.",
            'burn':    "Run cool (not cold) water over the burn for at least 20 minutes — this is the most important step. Cover loosely with cling film or a clean bag. Please don't use ice, butter, or toothpaste. For anything larger than your palm, go to the hospital.",
            'fever':   "A fever is your body fighting something — it means your immune system is working. Rest, keep drinking fluids, and take paracetamol to bring it down. If it goes above 39.5°C or you have a stiff neck or rash, please see a doctor today.",
            'headache': "Most headaches are from tension or dehydration, which is reassuring. Start with a big glass of water, rest somewhere quiet, and try a gentle neck stretch. If this one feels different from your usual headaches — especially very sudden or severe — I'd want you to get checked out.",
            'allergy': "First, get away from whatever triggered it. Antihistamines should help with mild symptoms like itching or a runny nose. But if your throat feels tight, you're wheezing, or your face is swelling — that's anaphylaxis and you need 999 right now.",
            'dizzy':   "Dizziness can be unsettling — please sit or lie down right now so you don't fall. Sip some water slowly. It's often just dehydration or a sudden drop in blood pressure. If it keeps happening or you feel one-sided weakness, let's get that checked out.",
            'anxiety': "I hear you, and what you're feeling is real. Take a slow, deep breath with me — in for 4 counts, hold for 4, out for 4. You're safe right now. Anxiety can make symptoms feel much worse than they are, but I want to make sure we address what's going on. What's been worrying you most?",
            'sleep':   "Poor sleep affects everything — your mood, immunity, even pain levels. Try keeping the same bedtime every night and avoiding your phone for an hour before bed. A cool, dark room makes a real difference. How long has sleep been a problem for you?",
        }

        for key, response in responses.items():
            if key in user_lower:
                return response

        return random.choice([
            "I'm here and I'm listening. Can you tell me a little more about what you're experiencing? The more you share, the better I can help.",
            "That's a good thing to bring up — your health matters. Could you describe what you're feeling in a bit more detail so I can give you the most helpful advice?",
            "I want to make sure I give you the right guidance. Can you tell me how long you've been feeling this way and whether anything makes it better or worse?",
            "I'm glad you reached out. Let's figure this out together — what symptoms are bothering you the most right now?",
        ])


gemini_service = GeminiService()