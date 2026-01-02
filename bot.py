import asyncio
import requests
from datetime import datetime
import os
import sys
from telegram import InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================

BOT_TOKEN = "8271752249:AAEZck5GOqdGZRODfCaixAYQbyxbD63-f7w"

API_URL = "https://shawonhax28.onrender.com/join?tc=1649094&uid1=14104810840&uid2=123&uid3=456&uid4=789&uid5=101&uid6=202&emote_id=909037004"

REQUEST_INTERVAL = 60        # 1 minute
HOURLY_RESTART = 3600        # 1 hour
LOG_FILE = "logs.txt"

# =======================================

start_time = datetime.now()

def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def send_api():
    try:
        r = requests.get(API_URL, timeout=15)
        log(f"API {r.status_code} | {r.text}")
    except Exception as e:
        log(f"API ERROR: {e}")

async def send_log(bot, chat_id):
    try:
        with open(LOG_FILE, "rb") as f:
            await bot.send_document(chat_id, InputFile(f), caption="📄 Logs")
    except Exception as e:
        log(f"LOG SEND ERROR: {e}")

async def worker(app, chat_id):
    global start_time
    while True:
        try:
            send_api()
            await send_log(app.bot, chat_id)

            if (datetime.now() - start_time).total_seconds() >= HOURLY_RESTART:
                log("HOURLY RESTART")
                os.execv(sys.executable, [sys.executable] + sys.argv)

            await asyncio.sleep(REQUEST_INTERVAL)
        except Exception as e:
            log(f"WORKER ERROR: {e}")
            await asyncio.sleep(5)

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot started.\nRunning every 1 minute.")
    context.application.create_task(worker(context.application, update.message.chat_id))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log(f"BOT CRASHED: {e}")
            asyncio.run(asyncio.sleep(5))
