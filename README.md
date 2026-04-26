# Erler Brain

**Personal AI Assistant on a small VPS — Telegram + WhatsApp + Claude + Google Workspace.**

Reference implementation. ~5 EUR/month. Your code, your data, your prompt.

---

## What it does

You message your bot on Telegram (or WhatsApp). The Brain figures out what you want, picks the right model, and either answers, searches your docs, drafts an email, or queues a high-stakes task for your approval.

| Feature | What it does |
|---|---|
| **Hybrid intent detection** | Regex first (free, fast), Gemini fallback for fuzzy intents |
| **Two-model routing** | Cheap Gemini Flash for high-volume tasks, Claude Sonnet for high-stakes drafts |
| **RAG over your docs** | FAISS vector index over Drive / Notion / local markdown |
| **Gmail integration** | Search inbox, read full thread, draft + send replies |
| **Google Drive search** | Find files by name or content, fetch text |
| **Calendar lookup** | "What's on today / tomorrow" |
| **WhatsApp via Evolution API** | Send + receive (self-hosted bridge) |
| **Per-contact rules** | YAML config: who gets the formal Sonnet draft, who gets the auto-reply |
| **Session memory** | S3-backed conversation history per user |

---

## Architecture

```
[Telegram] --long-poll--> main.py --> bot.router --> handlers/
                                                       |
                                                       +--> services/claude (high-stakes)
                                                       +--> services/gemini (default)
                                                       +--> services/gmail
                                                       +--> services/gdrive
                                                       +--> services/gcal
                                                       +--> services/rag (FAISS)
                                                       +--> services/whatsapp
                                                              |
                                                              v
[WhatsApp Cloud] --webhook--> webhook.server (aiohttp:8080)
```

`main.py` boots both the Telegram long-polling loop and an aiohttp webhook server in one process. Run it under `systemd` on a 1 GB Lightsail box and it costs about 5 EUR/month.

---

## Cost

| Component | Cost |
|---|---|
| AWS Lightsail (1 GB) | 5 EUR/month |
| Anthropic Claude API | ~3 EUR/month (low volume, only high-stakes) |
| Google Gemini Flash | ~free at personal volume |
| Telegram Bot | free |
| Evolution API (self-hosted) | optional, ~5 EUR/month if you add WhatsApp |
| **Total** | **~5-15 EUR/month** |

---

## Run it locally (15 minutes)

This walks you from zero to a working bot on your laptop. For production deployment on a VPS, see [SETUP.md](SETUP.md).

### Prerequisites

| Need | Where to get it | Required? |
|---|---|---|
| Python 3.10+ | [python.org/downloads](https://python.org/downloads) | yes |
| `git` | [git-scm.com](https://git-scm.com) | yes |
| Telegram account | The app | yes |
| Anthropic API key | [console.anthropic.com](https://console.anthropic.com) → Settings → API Keys | yes (for Claude) |
| Gemini API key | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | yes (free tier works) |
| Google OAuth (Gmail/Drive/Cal) | Google Cloud Console | optional |
| Evolution API instance | Self-hosted Docker | optional (WhatsApp only) |

### Step 1 — Create the Telegram bot (3 min)

1. In Telegram, open [@BotFather](https://t.me/BotFather)
2. Send `/newbot` → name it (e.g. `My Brain`) → copy the bot token (looks like `123456:ABCdef...`)
3. Open your new bot in Telegram and send any message — anything, just to register the chat
4. Keep the token handy for Step 4

### Step 2 — Clone and set up the environment (3 min)

```bash
git clone https://github.com/chris1928a/erler-brain-public.git
cd erler-brain-public

# Create an isolated Python environment
python -m venv .venv

# Activate it
source .venv/bin/activate          # macOS / Linux
# OR on Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Get your Telegram User ID (1 min)

Only YOUR user ID is allowed to talk to the bot — everyone else is silently rejected.

```bash
export TELEGRAM_BOT_TOKEN="123456:ABCdef..."   # your token from Step 1
python scripts/get_telegram_user_id.py
```

(Windows PowerShell: `$env:TELEGRAM_BOT_TOKEN="123456:ABCdef..."`)

You should see something like:
```
user_id=987654321  name=Chris Erler  username=@chris1928a
```

Copy the `user_id` — you'll paste it in the next step.

### Step 4 — Configure environment + personal context (3 min)

```bash
cp .env.example .env
cp config/rules.yaml.example config/rules.yaml
cp config/context.md.example config/context.md
```

Open `.env` in your editor and fill in at minimum:

```bash
TELEGRAM_BOT_TOKEN=123456:ABCdef...        # from Step 1
ALLOWED_USER_ID=987654321                  # from Step 3
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx       # from console.anthropic.com
GEMINI_API_KEY=AIzaSy...                   # from aistudio.google.com
```

Edit `config/context.md` — tell the Brain who you are, your ventures, your writing style. This becomes the system prompt for every Claude call.

Edit `config/rules.yaml` — define which contacts route to Claude (high-stakes drafts) vs. Gemini (auto-replies). Defaults work fine; tune later.

### Step 5 — Boot the Brain (1 min)

```bash
python main.py
```

You should see:
```
[erler-brain] INFO: Erler Brain v3 starting...
[telegram] INFO: Telegram bot configured with 9 handlers
[webhook] INFO: WhatsApp webhook server started on port 8080
[erler-brain] INFO: Erler Brain v3 running! Telegram + WhatsApp ready.
```

### Step 6 — Talk to it (30 sec)

Open Telegram, find your bot, and send `/start`. You should get the help text back with all the commands. Try:

- `/ask was ist eine MEDDIC qualification` → direct AI answer (Gemini)
- `/cal` → today's calendar (only works if you set up Google OAuth)
- `/status` → system health

To stop the bot: `Ctrl+C` in the terminal.

### Optional — Add Google Workspace (10 min)

If you want `/email`, `/drive`, `/cal` to actually work:

1. Set up a Google Cloud project: enable Gmail, Drive, Calendar APIs
2. Download Desktop OAuth credentials as `credentials.json` into the repo root
3. Run: `python scripts/get_google_refresh_token.py`
4. Paste the printed JSON into `.env` as `GOOGLE_CREDENTIALS_JSON`
5. Delete `credentials.json` (only the refresh token is needed)
6. Restart `python main.py`

### Optional — Build your RAG index (5 min)

So `/brain` can search your local docs:

```bash
python scripts/build_rag_index.py /path/to/your/markdown/docs
```

Walks the directory, chunks each markdown file by H2 heading, embeds via Gemini, writes a FAISS index to `.chunks/`. Re-run whenever your docs change.

---

## Run it as a service (production)

The local setup above is fine for testing. For 24/7 uptime, deploy to a 5 EUR/month Lightsail VPS and run under `systemd`. Full guide: [SETUP.md](SETUP.md).

Architecture rationale (why two-model routing, why YAML rules, why Lightsail vs Lambda): [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Bot does not respond | Wrong `ALLOWED_USER_ID` (silently rejects unauthorized users) | Re-run `scripts/get_telegram_user_id.py` and check `.env` |
| `KeyError: 'ANTHROPIC_API_KEY'` | `.env` not loaded or key missing | Check `.env` exists in repo root, key is set, no trailing spaces |
| `pip install` fails on `faiss-cpu` | Common on Apple Silicon | Try `pip install faiss-cpu --no-binary :all:` or skip RAG features |
| `/email` says "GOOGLE_CREDENTIALS_JSON not set" | OAuth step skipped | Either skip Google features, or do the optional Google setup above |
| Webhook port 8080 already in use | Another service holds the port | Edit `webhook/server.py` line 8 to a free port, or stop the other service |
| Logs show `Unauthorized.` | Someone else messaged your bot | Expected — only `ALLOWED_USER_ID` gets a real response |

---

## Skills

This repo ships with one Claude Code Skill in `skills/sherpa-gtm-sales-intelligence/` — the
Go-To-Market Intelligence skill that powers the [Sales Leadership Board](https://github.com/chris1928a/sales-leadership-board).
Together they tell a complete story: this is the brain, the Sales Board is what it built.

---

## See Also

- **[Sales Leadership Board](https://github.com/chris1928a/sales-leadership-board)** — CRM-to-coaching pipeline. The Brain reasons about GTM data using the Sherpa skill in this repo, the Sales Board is the runtime.
- **[Cape Town AI Exchange](https://github.com/chris1928a/cape-town-ai-exchange)** — quick-start guides and meetup notes for the Cape Town crew.

---

## License & Use

MIT. Fork it, gut it, make it yours. PRs welcome but optional — this is a reference, not a product.

If you build something interesting on top, ping me: chris@erlerventures.org.
