"""WhatsApp via Evolution API."""
import os
import logging
import requests

logger = logging.getLogger("whatsapp")

BASE_URL = os.environ.get("EVOLUTION_API_URL", "")
API_KEY = os.environ.get("EVOLUTION_API_KEY", "")
INSTANCE = os.environ.get("EVOLUTION_INSTANCE", "erler-brain")


async def send_message(number: str, text: str) -> str:
    """Send WhatsApp message via Evolution API."""
    if not BASE_URL:
        return "❌ Evolution API nicht konfiguriert"

    url = f"{BASE_URL}/message/sendText/{INSTANCE}"
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    payload = {
        "number": number,
        "text": text,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 201:
            return f"✅ WhatsApp gesendet an {number}"
        else:
            return f"❌ WhatsApp Fehler: {resp.status_code} — {resp.text[:200]}"
    except Exception as e:
        return f"❌ WhatsApp Error: {str(e)}"
