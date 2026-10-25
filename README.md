# NFTKNRenderSimple

Simple Telegram bot with Flask, deployable on Render.

## Setup

```bash
pip install -r requirements.txt
python app.py
Environment Variables
TELEGRAM_BOT_TOKEN

NFTOKEN_API_KEY

Deploy on Render
Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app

Endpoints
GET / — health check

POST /webhook — Telegram webhook
