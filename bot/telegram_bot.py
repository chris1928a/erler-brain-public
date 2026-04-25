"""Telegram Bot using python-telegram-bot v21+ (long-polling mode)"""
import logging
import os

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from bot.router import route_message
from bot.intent import detect_intent

logger = logging.getLogger("telegram")

ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


async def check_auth(update: Update) -> bool:
    """Only allow messages from the authorized user."""
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Unauthorized.")
        return False
    return True


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    help_text = """🧠 *Erler Brain v3*

*Commands:*
/brain [Frage] — Search brain (FAISS RAG)
/ask [Frage] — Direct AI (no docs)
/email [query] — Search Gmail
/email read [ID] — Read full email
/email draft [to] [subject] | [body] — Draft email
/drive [query] — Search Google Drive
/cal — Today's calendar
/cal tomorrow — Tomorrow's calendar
/wa [number] [text] — Send WhatsApp
/status — System health
/rules — Show routing rules

*Oder einfach schreiben* — ich erkenne automatisch was du willst."""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cmd_brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Usage: /brain [Frage]")
        return
    await update.message.reply_text("🔍 Searching brain...")
    from bot.handlers.brain import handle_brain
    response = await handle_brain(query, update.effective_user.id)
    await update.message.reply_text(response, parse_mode="Markdown")


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Usage: /ask [Frage]")
        return
    await update.message.reply_text("🤖 Thinking...")
    from bot.handlers.brain import handle_ask
    response = await handle_ask(query, update.effective_user.id)
    await update.message.reply_text(response, parse_mode="Markdown")


async def cmd_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    args = " ".join(context.args) if context.args else ""
    await update.message.reply_text("📧 Checking email...")
    from bot.handlers.email import handle_email
    response = await handle_email(args, update.effective_user.id)
    await update.message.reply_text(response, parse_mode="Markdown")


async def cmd_drive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    query = " ".join(context.args) if context.args else ""
    await update.message.reply_text("📁 Searching Drive...")
    from bot.handlers.drive import handle_drive
    response = await handle_drive(query, update.effective_user.id)
    await update.message.reply_text(response, parse_mode="Markdown")


async def cmd_cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    args = " ".join(context.args) if context.args else "today"
    await update.message.reply_text("📅 Checking calendar...")
    from bot.handlers.calendar import handle_calendar
    response = await handle_calendar(args, update.effective_user.id)
    await update.message.reply_text(response, parse_mode="Markdown")


async def cmd_wa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    args = " ".join(context.args) if context.args else ""
    from bot.handlers.whatsapp import handle_whatsapp_send
    response = await handle_whatsapp_send(args)
    await update.message.reply_text(response, parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    from bot.handlers.status import handle_status
    response = await handle_status()
    await update.message.reply_text(response, parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-text messages — auto-detect intent and route."""
    if not await check_auth(update):
        return

    text = update.message.text
    user_id = str(update.effective_user.id)

    # Load session history
    from services.session import load_session, add_message, save_session, format_history
    session = await load_session(user_id)
    add_message(session, "user", text)
    history = format_history(session)

    # Detect intent
    intent, params = await detect_intent(text, history=history)
    logger.info("Intent: %s, Params: %s", intent, params)

    # Route to appropriate handler
    response = await route_message(intent, params, text, user_id, history)

    # Save session
    add_message(session, "assistant", response[:500])
    await save_session(user_id, session)

    # Send response (split if too long)
    if len(response) > 4096:
        for i in range(0, len(response), 4096):
            await update.message.reply_text(response[i:i+4096], parse_mode="Markdown")
    else:
        await update.message.reply_text(response, parse_mode="Markdown")


def create_bot() -> Application:
    """Create and configure the Telegram bot application."""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("brain", cmd_brain))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(CommandHandler("email", cmd_email))
    app.add_handler(CommandHandler("drive", cmd_drive))
    app.add_handler(CommandHandler("cal", cmd_cal))
    app.add_handler(CommandHandler("wa", cmd_wa))
    app.add_handler(CommandHandler("status", cmd_status))

    # Free text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Telegram bot configured with %d handlers", len(app.handlers[0]))
    return app
