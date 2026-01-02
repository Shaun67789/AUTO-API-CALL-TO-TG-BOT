import requests
import logging
from datetime import datetime
import asyncio
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8271752249:AAEZck5GOqdGZRODfCaixAYQbyxbD63-f7w"  # <-- Put your Telegram bot token here

# Fixed UIDs (replace with your values)
UID2 = "123456"
UID3 = "234567"
UID4 = "345678"
UID5 = "456789"
UID6 = "567890"

# API URL
API_URL = "https://shawonhax28.onrender.com/join?tc=1649094&uid1=14104810840&uid2={uid2}&uid3={uid3}&uid4={uid4}&uid5={uid5}&uid6={uid6}&emote_id=909037004"

# =========================
# Logging setup
# =========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# =========================
# API request function
# =========================
def send_request():
    url = API_URL.format(uid2=UID2, uid3=UID3, uid4=UID4, uid5=UID5, uid6=UID6)
    try:
        response = requests.get(url, timeout=15)
        status = response.status_code
        text = response.text
    except Exception as e:
        status = "ERROR"
        text = str(e)

    log_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Status: {status} | Response: {text}\n"
    
    # Save log
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(log_line)
    
    return log_line

# =========================
# Bot commands
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Auto emote sender started! Sending request every 1 minute..."
    )

    # Start loop task
    context.application.create_task(loop_emote(context, update.message.chat_id))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(context.application, "emote_task"):
        context.application.emote_task.cancel()
        await update.message.reply_text("⏹️ Auto emote sender stopped.")
    else:
        await update.message.reply_text("No running task found.")

# =========================
# Loop task
# =========================
async def loop_emote(context, chat_id):
    try:
        while True:
            log_line = send_request()
            print(log_line.strip())
            
            # Send updated log file to Telegram
            with open("logs.txt", "rb") as f:
                await context.bot.send_document(chat_id=chat_id, document=InputFile(f), caption="📄 Latest API logs")
            
            await asyncio.sleep(60)  # wait 1 minute
    except asyncio.CancelledError:
        print("Loop task cancelled.")

# =========================
# Main
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    print("Bot is running...")
    app.run_polling()