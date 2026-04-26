#!/usr/bin/env python3
"""
Get your numeric Telegram user ID for the ALLOWED_USER_ID env var.

Usage:
    1. Send any message to your bot in Telegram
    2. Run: TELEGRAM_BOT_TOKEN=<your-token> python scripts/get_telegram_user_id.py
    3. Copy the user_id printed and paste into .env as ALLOWED_USER_ID
"""
import os
import sys

import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    sys.exit("Set TELEGRAM_BOT_TOKEN env var first (e.g. export TELEGRAM_BOT_TOKEN=...)")

resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10)
resp.raise_for_status()
updates = resp.json().get("result", [])

if not updates:
    sys.exit(
        "No updates found. Send any message to your bot first, then re-run.\n"
        "(Telegram only delivers updates that arrived AFTER the last getUpdates call,\n"
        "so if this is empty, send a fresh message and try again.)"
    )

seen = set()
for upd in updates:
    msg = upd.get("message") or upd.get("edited_message") or {}
    user = msg.get("from", {})
    uid = user.get("id")
    if uid and uid not in seen:
        seen.add(uid)
        name = user.get("first_name", "?") + " " + user.get("last_name", "")
        username = "@" + user.get("username", "noname")
        print(f"user_id={uid:<12} name={name.strip():<25} username={username}")

print(f"\nFound {len(seen)} unique user(s).")
print("Copy the user_id you want to authorize into .env as ALLOWED_USER_ID.")
