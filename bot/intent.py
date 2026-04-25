"""Hybrid intent detection: Regex fast-path + Gemini AI fallback."""
import re
import logging

logger = logging.getLogger("intent")


def detect_intent_regex(text: str) -> tuple:
    """Fast regex-based intent detection. Returns (intent, params) or (None, None)."""
    t = text.strip().lower()

    # Email patterns
    if re.match(r"(check|zeig|show|lies|fass).*(mail|email|inbox)", t):
        return ("email_search", {"query": "is:unread"})
    if re.match(r"(mail|email).*(such|find|search)", t):
        return ("email_search", {"query": t})
    if m := re.match(r"(draft|schreib|write).*(mail|email)", t):
        return ("email_draft", {"args": text})

    # Calendar patterns
    if re.match(r"(kalender|calendar|termin|meeting|was steht)", t):
        if "morgen" in t or "tomorrow" in t:
            return ("calendar", {"query": "tomorrow"})
        return ("calendar", {"query": "today"})

    # Drive patterns
    if re.match(r"(drive|datei|file|dokument|such.*drive)", t):
        return ("drive_search", {"query": text})

    # WhatsApp patterns
    if re.match(r"(whatsapp|wa |schick.*whatsapp|send.*whatsapp)", t):
        return ("whatsapp", {"args": text})

    # Status
    if t in ("status", "/status", "health", "wie geht es dir"):
        return ("status", {})

    return (None, None)


async def detect_intent_ai(text: str, history: str = "") -> tuple:
    """AI-based intent detection using Gemini Flash."""
    from services.gemini import call_gemini_direct
    import json

    prompt = f"""Classify this user message into one intent. The user is Christoph Erler, a founder/advisor.

Message: "{text}"

Recent conversation: {history[-500:] if history else "(none)"}

Intents:
- email_search: User wants to check/search emails
- email_read: User wants to read a specific email
- email_draft: User wants to draft/write/reply to an email
- drive_search: User wants to search Google Drive
- calendar: User wants to check calendar/meetings
- whatsapp: User wants to send WhatsApp message
- brain: User wants to search their knowledge base
- content: User wants to create content (LinkedIn, newsletter, etc.)
- status: User wants system status
- general: General question/conversation

Return ONLY a JSON object: {{"intent": "...", "params": {{}}}}
If email_search, add "query" to params.
If calendar, add "query": "today" or "tomorrow" to params."""

    try:
        response = await call_gemini_direct(prompt)
        data = json.loads(response)
        return (data.get("intent", "general"), data.get("params", {}))
    except Exception as e:
        logger.warning("AI intent detection failed: %s", str(e))
        return ("general", {})


async def detect_intent(text: str, history: str = "") -> tuple:
    """Hybrid: regex first (fast), AI fallback (smart)."""
    intent, params = detect_intent_regex(text)
    if intent is not None:
        logger.info("Intent (regex): %s", intent)
        return (intent, params)

    intent, params = await detect_intent_ai(text, history=history)
    logger.info("Intent (AI): %s", intent)
    return (intent, params)
