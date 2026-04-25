"""aiohttp webhook server for incoming WhatsApp messages → forwarded to Telegram."""
import json
import logging
from aiohttp import web

logger = logging.getLogger("webhook")

WEBHOOK_PORT = 8080
_bot_app = None


async def handle_whatsapp_webhook(request):
    """Handle incoming WhatsApp messages from Evolution API."""
    try:
        data = await request.json()
        event = data.get("event", "")

        if event == "messages.upsert":
            messages = data.get("data", [])
            if isinstance(messages, dict):
                messages = [messages]

            for msg in messages:
                if msg.get("key", {}).get("fromMe"):
                    continue  # Skip own messages

                sender = msg.get("key", {}).get("remoteJid", "unknown")
                push_name = msg.get("pushName", "Unknown")
                text = ""

                if "message" in msg:
                    text = (
                        msg["message"].get("conversation", "") or
                        msg["message"].get("extendedTextMessage", {}).get("text", "")
                    )

                if text:
                    # Log incoming WhatsApp messages but do NOT auto-forward to Telegram
                    logger.info("WhatsApp received from %s: %s", push_name, text[:80])

        return web.json_response({"status": "ok"})

    except Exception as e:
        logger.error("Webhook error: %s", str(e))
        return web.json_response({"error": str(e)}, status=500)


async def start_webhook_server(bot_app):
    """Start aiohttp webhook server."""
    global _bot_app
    _bot_app = bot_app

    app = web.Application()
    app.router.add_post("/webhook/whatsapp", handle_whatsapp_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    logger.info("WhatsApp webhook server started on port %d", WEBHOOK_PORT)
