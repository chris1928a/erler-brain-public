# Setup — Erler Brain on AWS Lightsail

Deploy in about 30 minutes. Total cost: 5 EUR/month for the VPS, plus API usage (~3-10 EUR/month).

---

## Prerequisites

- AWS account (Lightsail is the simplest VPS option, but any 1 GB Linux box works: DigitalOcean, Hetzner, etc.)
- Telegram account
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Google AI Studio API key for Gemini ([aistudio.google.com/apikey](https://aistudio.google.com/apikey))
- (Optional) Google Cloud project with Gmail / Drive / Calendar APIs enabled
- (Optional) Self-hosted Evolution API for WhatsApp

---

## Step 1: Create the Telegram bot

1. In Telegram, message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token (looks like `123456:ABCdef...`)
4. Send any message to your new bot, then visit
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` and copy your numeric `chat.id`

---

## Step 2: Provision the VPS

In the AWS Lightsail console:

1. Create instance → Linux/Unix → OS only → Ubuntu 22.04
2. Instance plan: **5 USD/month** (1 GB RAM, 2 vCPU, 40 GB SSD) — sufficient
3. Name it `erler-brain` and launch
4. Networking → attach a static IP (free while attached)
5. Firewall: open TCP **22** (SSH), TCP **8080** (WhatsApp webhook, only if you use it)

SSH in:
```bash
ssh -i your-lightsail-key.pem ubuntu@<your-static-ip>
```

---

## Step 3: Install Python and clone the repo

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv git
git clone https://github.com/chris1928a/erler-brain-public.git
cd erler-brain-public
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step 4: Configure secrets

```bash
cp .env.example .env
nano .env
```

Fill in at minimum:
- `TELEGRAM_BOT_TOKEN` (from @BotFather)
- `ALLOWED_USER_ID` (your numeric Telegram ID)
- `ANTHROPIC_API_KEY` and/or `GEMINI_API_KEY`

Optional (Google Workspace):
- `GOOGLE_CREDENTIALS_JSON` — see [Google OAuth setup](#optional-google-workspace-oauth) below

---

## Step 5: Customize routing and context

```bash
cp config/rules.yaml.example config/rules.yaml
cp config/context.md.example config/context.md
nano config/rules.yaml         # who gets Claude vs Gemini, auto-reply patterns
nano config/context.md         # tell the Brain about your ventures and writing style
```

---

## Step 6: First run

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

In Telegram, message your bot: `/start`. You should get the help text back.

---

## Step 7: Run as a systemd service

So the Brain restarts on reboot or crash:

```bash
sudo nano /etc/systemd/system/erler-brain.service
```

Paste:
```ini
[Unit]
Description=Erler Brain
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/erler-brain-public
EnvironmentFile=/home/ubuntu/erler-brain-public/.env
ExecStart=/home/ubuntu/erler-brain-public/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activate:
```bash
sudo systemctl daemon-reload
sudo systemctl enable erler-brain
sudo systemctl start erler-brain
sudo systemctl status erler-brain         # check it is running
journalctl -u erler-brain -f               # tail logs
```

Done. Your Brain is live.

---

## Optional: Google Workspace OAuth

To enable `/email`, `/drive`, `/cal`:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project, enable Gmail API + Drive API + Calendar API
3. Create OAuth 2.0 credentials (Desktop application type)
4. Download `credentials.json`
5. Run a one-off script to get a refresh token (see `scripts/get_google_refresh_token.py` —
   you can write this in 20 lines using `google-auth-oauthlib.InstalledAppFlow`)
6. Paste the resulting JSON (single line) into `GOOGLE_CREDENTIALS_JSON` in `.env`

---

## Optional: WhatsApp via Evolution API

Self-host [Evolution API](https://github.com/EvolutionAPI/evolution-api) (Docker, ~5 EUR/month
on the same VPS or a separate one). Configure the webhook URL to point at
`http://<your-static-ip>:8080/webhook/whatsapp`. Then fill in the `EVOLUTION_*` variables in `.env`.

---

## Troubleshooting

- **Bot does not respond**: check `journalctl -u erler-brain -f`. Most common cause is wrong
  `ALLOWED_USER_ID` (the bot silently rejects unauthorized users).
- **Claude / Gemini errors**: check API keys and rate limits in their respective dashboards.
- **Webhook not reachable**: open TCP 8080 in the Lightsail firewall, and use `http://` (not `https`)
  if you have not set up TLS.
