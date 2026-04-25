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

## Quick Start

```bash
git clone https://github.com/chris1928a/erler-brain-public.git
cd erler-brain-public
pip install -r requirements.txt
cp .env.example .env                              # fill in your tokens
cp config/rules.yaml.example config/rules.yaml    # edit your routing rules
cp config/context.md.example config/context.md    # add your personal context
python main.py
```

Detailed deployment guide: see [SETUP.md](SETUP.md).
Architecture deep dive: see [ARCHITECTURE.md](ARCHITECTURE.md).

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
