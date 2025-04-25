import os
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_TOKEN
from database import init_db
from handlers import start, add_item, list_items, delete_item

async def main():
    init_db()  # راه‌اندازی دیتابیس
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ثبت دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("delete", delete_item))

    # تنظیم webhook برای Heroku
    PORT = int(os.environ.get("PORT", 8443))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")  # در Heroku تنظیم می‌شه
    webhook_url = f"https://{HEROKU_APP_NAME}.herokuapp.com/{TELEGRAM_TOKEN}"

    await app.bot.set_webhook(webhook_url)
    print(f"Webhook تنظیم شد: {webhook_url}")

    # شروع ربات با webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
