#!/usr/bin/env python3
"""
One-off script to get a Google OAuth refresh token for Gmail / Drive / Calendar.

Prerequisites:
    1. Google Cloud project with Gmail, Drive, Calendar APIs enabled
    2. OAuth 2.0 Desktop credentials downloaded as credentials.json
       (Cloud Console -> APIs & Services -> Credentials -> Create -> OAuth client ID -> Desktop)
    3. pip install google-auth-oauthlib

Usage:
    python scripts/get_google_refresh_token.py

A browser window opens, you authorize, and the script prints a single-line JSON
that you paste into .env as GOOGLE_CREDENTIALS_JSON.
"""
import json
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    sys.exit("pip install google-auth-oauthlib")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

CREDS_PATH = Path("credentials.json")
if not CREDS_PATH.exists():
    sys.exit(
        "credentials.json not found. Download Desktop OAuth credentials from\n"
        "Google Cloud Console and place them in the project root as credentials.json."
    )

flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
creds = flow.run_local_server(port=0)

with CREDS_PATH.open() as f:
    desktop = json.load(f)["installed"]

payload = {
    "refresh_token": creds.refresh_token,
    "client_id": desktop["client_id"],
    "client_secret": desktop["client_secret"],
}

print("\n" + "=" * 70)
print("Paste this single-line JSON into .env as GOOGLE_CREDENTIALS_JSON:")
print("=" * 70)
print(json.dumps(payload))
print("=" * 70)
print("\nDelete credentials.json after this — only the refresh_token is needed.")
