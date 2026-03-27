import re
from django.conf import settings
from groq import Groq, APIConnectionError, BadRequestError, AuthenticationError
import google.generativeai as genai


CRISIS_PATTERNS = [
    r"\bkill myself\b",
    r"\bsuicide\b",
    r"\bend my life\b",
    r"\bself[- ]harm\b",
    r"\bhurt myself\b",
]


def is_crisis(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(pattern, t) for pattern in CRISIS_PATTERNS)


CRISIS_REPLY = (
    "I’m really sorry you’re feeling this way. You don’t have to handle this alone.\n\n"
    "If you feel you might hurt yourself or you’re in immediate danger, please call your local emergency number now.\n"
    "In India, you can call 112 (emergency). You can also reach AASRA at 91-22-27546669.\n\n"
    "If you can, tell me: are you safe right now?"
)


SYSTEM_PROMPT = (
    "You are a calm, supportive mental wellness companion. "
    "Respond with empathy and validation. "
    "Ask one short follow-up question. "
    "Do not diagnose medical conditions.\n\n"
    "Based on the user's feelings, suggest a specific activity from our app that could help them feel better. "
    "Activities you can suggest include: 'Try a 5-minute breathing exercise', "
    "'Listen to some calming nature sounds or music therapy', "
    "'Do a quick mood check-in', "
    "'Write down your thoughts in the journal', "
    "'Read your daily affirmation', or "
    "'Try a guided body scan meditation'.\n\n"
    "If CONTEXT is provided, use it when relevant."
)


def build_prompt(user_message: str, history: list[dict], context: str = "") -> str:
    prompt = SYSTEM_PROMPT + "\n\n"

    if context:
        prompt += f"CONTEXT:\n{context}\n\n"

    if history:
        prompt += "CHAT HISTORY:\n"
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role}: {content}\n"

    prompt += f"user: {user_message}\nassistant:"
    return prompt


def generate_reply(user_message: str, history: list[dict], context: str = "") -> str:
    print("AI DEBUG -> GEMINI_API_KEY:", repr(getattr(settings, "GEMINI_API_KEY", None)))
    print("AI DEBUG -> GEMINI_MODEL:", repr(getattr(settings, "GEMINI_MODEL", None)))
    print("AI DEBUG -> GROQ_API_KEY:", repr(getattr(settings, "GROQ_API_KEY", None)))

    if is_crisis(user_message):
        return CRISIS_REPLY

    prompt = build_prompt(user_message, history, context)

    gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)
    gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")

    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(gemini_model)
            response = model.generate_content(prompt)

            if hasattr(response, "text") and response.text:
                return response.text.strip()

            return "Gemini returned an empty response."

        except Exception as e:
            print("Gemini error:", str(e))
            return f"Gemini error: {str(e)}"

    groq_api_key = getattr(settings, "GROQ_API_KEY", None)
    groq_model = getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant")

    if groq_api_key:
        try:
            client = Groq(api_key=groq_api_key)

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            if context:
                messages.append({"role": "system", "content": f"CONTEXT:\n{context}"})

            if history:
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role in ["system", "user", "assistant"] and content:
                        messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": user_message})

            resp = client.chat.completions.create(
                model=groq_model,
                messages=messages,
                temperature=0.6,
                max_tokens=250,
            )

            return resp.choices[0].message.content.strip()

        except BadRequestError as e:
            return f"Groq model error. Check GROQ_MODEL. Details: {e}"
        except AuthenticationError:
            return "Groq API key is invalid. Regenerate key in Groq Console and update .env"
        except APIConnectionError:
            return "Cannot reach Groq API (internet/DNS issue). Try hotspot or change network."
        except Exception as e:
            return f"Groq AI error: {str(e)}"

    return "No AI key configured. Set GEMINI_API_KEY or GROQ_API_KEY in .env"