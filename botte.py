import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Загружаем ключи из .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

if not BOT_TOKEN or not APP_URL:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN or APP_URL not set in .env")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Открыть мини-апку", url=APP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми кнопку ниже 👇", reply_markup=reply_markup)

# Основная функция
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
