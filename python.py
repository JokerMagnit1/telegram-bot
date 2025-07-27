from telegram import Update
from telegram.ext import (
  ApplicationBuilder,
  MessageHandler,
  filters,
  ContextTypes
)

TOKEN = '8098721049:AAGRrKEbOnqsAKDubJqVGX-x9R4vhcPxv_Y'
OWNER_CHAT_ID = 5827840288  # замените на свой chat_id
users: dict[int, int] = {}   # user_id → chat_id

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

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
      MessageHandler(
        filters.TEXT & ~filters.Chat(OWNER_CHAT_ID),
        forward_to_owner
      )
    )
    app.add_handler(
      MessageHandler(
        filters.Chat(OWNER_CHAT_ID) & filters.REPLY,
        reply_from_owner
      )
    )

    app.run_polling()

if __name__ == '__main__':
    main()