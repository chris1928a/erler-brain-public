"""Route messages to the right AI model and handler based on intent + rules."""
import logging
import yaml
from pathlib import Path

logger = logging.getLogger("router")

# Load rules
RULES_PATH = Path(__file__).parent.parent / "config" / "rules.yaml"


def load_rules():
    with open(RULES_PATH) as f:
        return yaml.safe_load(f)

RULES = load_rules()
HIGH_STAKES_KEYWORDS = RULES.get("tasks", {}).get("high_stakes_keywords", [])


def select_model(text: str, intent: str) -> str:
    """Select AI model based on content and intent."""
    text_lower = text.lower()

    # High-stakes keywords → Claude
    if any(kw.lower() in text_lower for kw in HIGH_STAKES_KEYWORDS):
        return "claude-sonnet-4-6"

    # Content creation → Claude
    if intent in ("content", "draft_email", "linkedin"):
        return "claude-sonnet-4-6"

    # Everything else → Gemini Flash
    return "gemini-flash"


async def route_message(intent: str, params: dict, text: str, user_id: str, history: str = "") -> str:
    """Route a detected intent to the appropriate handler."""
    model = select_model(text, intent)
    logger.info("Routing: intent=%s, model=%s", intent, model)

    if intent == "email_search":
        from bot.handlers.email import handle_email
        return await handle_email(params.get("query", text), user_id)

    elif intent == "email_read":
        from bot.handlers.email import handle_email
        return await handle_email(f"read {params.get('id', '')}", user_id)

    elif intent == "email_draft":
        from bot.handlers.email import handle_email
        return await handle_email(f"draft {params.get('args', text)}", user_id)

    elif intent == "drive_search":
        from bot.handlers.drive import handle_drive
        return await handle_drive(params.get("query", text), user_id)

    elif intent == "calendar":
        from bot.handlers.calendar import handle_calendar
        return await handle_calendar(params.get("query", "today"), user_id)

    elif intent == "whatsapp":
        from bot.handlers.whatsapp import handle_whatsapp_send
        return await handle_whatsapp_send(params.get("args", text))

    elif intent == "brain":
        from bot.handlers.brain import handle_brain
        return await handle_brain(params.get("query", text), user_id)

    elif intent == "status":
        from bot.handlers.status import handle_status
        return await handle_status()

    else:
        # Default: smart search (brain + direct AI)
        from bot.handlers.brain import handle_smart
        return await handle_smart(text, user_id, history=history, model=model)
