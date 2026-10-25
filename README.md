# NFTKNRenderSimple

Simple Telegram bot with Flask, deployable on Render.

## Setup

```bash
pip install -r requirements.txt
python app.py

Environment Variables
TELEGRAM_BOT_TOKEN
NFTOKEN_API_KEY
AUTHORIZED_USERS (আপনার Telegram numeric ID, কমা দিয়ে একাধিক)


Deploy on Render
Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app

Endpoints
GET / — health check

POST /webhook — Telegram webhook


curl "https://api.telegram.org/bot8922491812:xyz/setWebhook?url=https://nftknrendersimple-1.onrender.com/webhook"
https://api.telegram.org/bot8922491812:xyz/setWebhook?url=https://nftknrendersimple-1.onrender.com/webhook
