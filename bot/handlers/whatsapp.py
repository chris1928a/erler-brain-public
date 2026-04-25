"""WhatsApp send handler."""
from services.whatsapp import send_message


async def handle_whatsapp_send(args: str) -> str:
    parts = args.strip().split(" ", 1)
    if len(parts) < 2:
        return "Usage: /wa [Nummer] [Nachricht]"
    number = parts[0]
    text = parts[1]
    return await send_message(number, text)
