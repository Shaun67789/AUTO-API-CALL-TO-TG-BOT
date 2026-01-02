import asyncio
import requests
import logging
from datetime import datetime
import os
import sys
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==================== CONFIG ====================

BOT_TOKEN = "8271752249:AAEZck5GOqdGZRODfCaixAYQbyxbD63-f7w"

API_URL = "https://shawonhax28.onrender.com/join?tc=1649094&uid1=14104810840&uid2=123&uid3=456&uid4=789&uid5=101&uid6=202&emote_id=909037004"

REQUEST_INTERVAL = 60          # 1 minute
HOURLY_RESTART_TIME = 3600     # 1 hour
LOG_FILE = "logs.txt"

# ===============================================

logging.basicConfig(level=logging.INFO)

start_time = datetime.now()

def log(text):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{time_now}] {text}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def send_api_request():
    try:
        response = requests.get(API_URL, timeout=15)
        log(f"API Status: {response.status_code} | Response: {response.text}")
    except Exception as e:
        log(f"API ERROR: {e}")

async def send_log_to_telegram(bot, chat_id):
    try:
        with open(LOG_FILE, "rb") as f:
            await bot.send_document(chat_id=chat_id, document=InputFile(f), caption="📄 Latest Log")
    except Exception as e:
        log(f"Log Send Error: {e}")

async def main_loop(app, chat_id):
    global start_time

    while True:
        try:
            send_api_request()
            await send_log_to_telegram(app.bot, chat_id)

            # Hourly self restart
            if (datetime.now() - start_time).total_seconds() >= HOURLY_RESTART_TIME:
                log("Hourly restart triggered.")
                os.execv(sys.executable, [sys.executable] + sys.argv)

            await asyncio.sleep(REQUEST_INTERVAL)

        except Exception as e:
            log(f"CRASH: {e}")
            await asyncio.sleep(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot started.\nAPI will run every 1 minute.")
    context.application.create_task(main_loop(context.application, update.message.chat_id))

# ==================== RUN BOT ====================

async def run():
    while True:
        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            log("Bot running...")
            await app.initialize()
            await app.start()
            await app.bot.initialize()
            await asyncio.Event().wait()
        except Exception as e:
            log(f"BOT CRASHED: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run())    app.run_polling()
