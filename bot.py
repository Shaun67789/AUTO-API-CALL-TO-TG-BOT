import asyncio
import requests
import logging
from datetime import datetime
import os
import sys
from telegram import InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==================== CONFIG ====================

BOT_TOKEN = "8271752249:AAEZck5GOqdGZRODfCaixAYQbyxbD63-f7w"

API_URL = "https://shawonhax28.onrender.com/join?tc=1649094&uid1=14104810840&uid2=123&uid3=456&uid4=789&uid5=101&uid6=202&emote_id=909037004"

REQUEST_INTERVAL = 60
HOURLY_RESTART_TIME = 3600
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
        r = requests.get(API_URL, timeout=15)
        log(f"API {r.status_code} | {r.text}")
    except Exception as e:
        log(f"API ERROR: {e}")

async def send_log(bot, chat_id):
    try:
        with open(LOG_FILE, "rb") as f:
            await bot.send_document(chat_id, InputFile(f), caption="📄 API Logs")
    except Exception as e:
        log(f"LOG SEND ERROR: {e}")

async def background_loop(app, chat_id):
    global start_time
    while True:
        try:
            send_api_request()
            await send_log(app.bot, chat_id)

            if (datetime.now() - start_time).total_seconds() >= HOURLY_RESTART_TIME:
                log("HOURLY RESTART")
                os.execv(sys.executable, [sys.executable] + sys.argv)

            await asyncio.sleep(REQUEST_INTERVAL)
        except Exception as e:
            log(f"LOOP ERROR: {e}")
            await asyncio.sleep(5)

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot activated.\nRunning API every 1 minute.")
    context.application.create_task(background_loop(context.application, update.message.chat_id))

async def main():
    while True:
        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            await app.run_polling()
        except Exception as e:
            log(f"BOT CRASHED: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
