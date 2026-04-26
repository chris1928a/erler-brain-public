# Helper scripts

One-off utilities for setting up the Brain. None of these run as part of the daily loop.

| Script | Purpose | Run when |
|---|---|---|
| `get_telegram_user_id.py` | Find your numeric Telegram user ID for `ALLOWED_USER_ID` | Once, during initial setup |
| `get_google_refresh_token.py` | Generate a refresh token for `GOOGLE_CREDENTIALS_JSON` | Once, when adding Gmail/Drive/Calendar |
| `build_rag_index.py` | Build a FAISS vector index over your local markdown docs | Whenever your source docs change |

Each script has a docstring at the top with usage instructions.
