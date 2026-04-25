# Architecture

Why each piece is the way it is. Not a tour of files — read the code for that.

---

## Design principles

1. **Two-model routing.** Most messages are cheap and routine ("what's on today", "search Drive for X").
   Send them to Gemini Flash. The few high-stakes drafts (contracts, investor email, legal) go to
   Claude Sonnet. This keeps API spend below 5 EUR/month at personal volume.

2. **Regex-first intent detection.** Before paying for an LLM intent classifier, run a fast
   regex pass (`bot/intent.py:detect_intent_regex`). About 80% of personal messages match a
   keyword pattern (mail/email/calendar/drive). The other 20% fall through to a Gemini call.

3. **YAML rules over hardcoded logic.** Per-contact behaviour (who gets Claude, who gets
   auto-reply, what counts as high-stakes) lives in `config/rules.yaml`. Editing the YAML
   does not require touching code.

4. **Single process, two transports.** Telegram and WhatsApp run in one Python process via
   `asyncio`. Telegram uses long-polling (no inbound port needed for that). WhatsApp uses an
   aiohttp webhook on port 8080. Both share session state and routing logic.

5. **Personal context in markdown, not code.** `config/context.md` is loaded as the system
   prompt. Edit your bio / ventures / writing style in plain markdown — the Brain picks it up
   on next start.

---

## Component map

```
main.py
 |
 +-- bot.telegram_bot
 |    |
 |    +-- bot.intent          (regex + Gemini intent detection)
 |    +-- bot.router          (route by intent + select_model)
 |    +-- bot.handlers/
 |         +-- brain.py        (RAG via FAISS, then Gemini answer)
 |         +-- email.py        (Gmail search/read/draft via google-api-python-client)
 |         +-- drive.py        (Drive search via google-api-python-client)
 |         +-- calendar.py     (Calendar via gcal service)
 |         +-- whatsapp.py     (Evolution API send)
 |         +-- status.py       (health check)
 |
 +-- webhook.server
      |
      +-- POST /webhook/whatsapp  (Evolution API events: messages.upsert, etc.)
```

---

## Why not Lambda / serverless?

The original `erler-brain` (private, AWS Lambda + EventBridge + SAM) worked but had three frictions:

- Cold starts hurt the bot UX. A 2-second response delay on every Telegram reply feels broken.
- Long-polling Telegram does not fit Lambda's request-response model.
- Iterating in production meant `sam build && sam deploy` for every prompt tweak.

The Lightsail process is `git pull && systemctl restart erler-brain`. Tradeoff: you maintain a VPS.
For a personal assistant, this tradeoff is worth it. For a multi-tenant product, it is not.

---

## Why FAISS for RAG?

A single user with a few thousand markdown / PDF files does not need a vector database service.
FAISS in-process (~100 MB index) is fast, free, and persists to disk. If the index grows past
~1 GB, switch to a managed service (Pinecone, Weaviate, pgvector).

The indexer (not in this repo — it is a separate one-off script) walks your Drive, chunks markdown
by heading, embeds with Gemini, and writes a FAISS index plus a chunks pickle. `services/rag.py`
loads both at startup.

---

## Session storage

`services/session.py` keeps the last N messages per user. Two backends:
- Local JSON file (default, fine for one user)
- S3 bucket if `SESSION_BUCKET` is set (useful if you run multiple Brain instances)

The session is read on every message and written after every response. Keep it small (last
20 messages) — long histories blow up token costs and rarely improve answers.

---

## Adding a new intent

1. Add a regex pattern in `bot/intent.py:detect_intent_regex` (or trust the AI fallback)
2. Add an `elif intent == "your_intent"` branch in `bot/router.py:route_message`
3. Create `bot/handlers/your_intent.py` with `async def handle_your_intent(...)`
4. Add a Telegram command in `bot/telegram_bot.py:create_bot` if you want a `/cmd` shortcut

That is the whole pattern. Resist adding abstractions until you have three handlers that
genuinely share logic.

---

## Skills

`skills/sherpa-gtm-sales-intelligence/` is a [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills.md)
— a markdown file plus references that any Claude Code session can load to gain GTM expertise.
The skill is the *meta-instruction* (how Claude reasons about CRM data); the runtime that
executes that reasoning is the [Sales Leadership Board](https://github.com/chris1928a/sales-leadership-board)
in a separate repo.

This repo ships the skill so the Brain can act as a Sales Coach when asked. Drop more skills
into `skills/` to extend its expertise.
