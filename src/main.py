from telegram.ext import Application, CommandHandler
from config import TELEGRAM_TOKEN
from database import init_db
from handlers import start, add_item, list_items, delete_item

def main():
    init_db()  # راه‌اندازی دیتابیس
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ثبت دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("delete", delete_item))

    print("ربات در حال اجرا است...")
    app.run_polling()

if __name__ == "__main__":
    main()
