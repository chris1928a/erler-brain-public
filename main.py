#!/usr/bin/env python3
"""Erler Brain v3 — Lightsail Orchestrator
Telegram Bot + WhatsApp Webhook + Cron Jobs
"""
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / "logs" / "bot.log"),
    ],
)
logger = logging.getLogger("erler-brain")

from bot.telegram_bot import create_bot
from webhook.server import start_webhook_server


async def main():
    logger.info("Erler Brain v3 starting...")

    # Start Telegram Bot (long-polling)
    bot_app = create_bot()

    # Start WhatsApp Webhook server (aiohttp on port 8080)
    webhook_task = asyncio.create_task(start_webhook_server(bot_app))

    # Start Telegram polling
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(drop_pending_updates=True)

    logger.info("Erler Brain v3 running! Telegram + WhatsApp ready.")

    # Keep running until killed
    stop_event = asyncio.Event()

    def handle_signal(sig, frame):
        logger.info("Received signal %s, shutting down...", sig)
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    await stop_event.wait()

    # Cleanup
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()
    webhook_task.cancel()
    logger.info("Erler Brain v3 stopped.")


if __name__ == "__main__":
    asyncio.run(main())
