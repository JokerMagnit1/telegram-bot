import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

# Настройки
TOKEN = os.environ["TELEGRAM_TOKEN"]
OWNER_CHAT_ID = int(os.environ["OWNER_CHAT_ID"])
users: dict[int, int] = {}

# Flask для health-check
app = Flask(__name__)

@app.route("/")
def health():
    return "OK", 200

# Telegram-бот
async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = update.effective_chat.id
    text = update.message.text or '<мультимедиа>'
    await context.bot.send_message(
        chat_id=OWNER_CHAT_ID,
        text=f"Сообщение от {user_id}:\n{text}"
    )

async def reply_from_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != OWNER_CHAT_ID or not update.message.reply_to_message:
        return
    first_line = update.message.reply_to_message.text.splitlines()[0]
    target_id = int(first_line.split()[2].strip(':'))
    reply_text = update.message.text
    if target_id in users:
        await context.bot.send_message(chat_id=users[target_id], text=reply_text)

def run_bot():
    app_tg = ApplicationBuilder().token(TOKEN).build()
    app_tg.add_handler(
        MessageHandler(filters.TEXT & ~filters.Chat(OWNER_CHAT_ID), forward_to_owner)
    )
    app_tg.add_handler(
        MessageHandler(filters.Chat(OWNER_CHAT_ID) & filters.REPLY, reply_from_owner)
    )
    app_tg.run_polling()

if __name__ == '__main__':
    # Запускаем одновременно Flask и Telegram-бота
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()
    run_bot()