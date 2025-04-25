import os
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_TOKEN
from database import init_db
from handlers import start, add_item, list_items, delete_item
import asyncio

async def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("delete", delete_item))

    PORT = int(os.environ.get("PORT", 8000))
    RENDER_APP_NAME = os.environ.get("RENDER_APP_NAME")
    webhook_url = f"https://{RENDER_APP_NAME}.onrender.com/{TELEGRAM_TOKEN}"

    print(f"Webhook تنظیم شد: {webhook_url}")
    await app.bot.set_webhook(webhook_url)

    # استفاده از start_webhook به جای run_webhook
    await app.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=f"/{TELEGRAM_TOKEN}",
        webhook_url=webhook_url
    )
    return app

if __name__ == "__main__":
    # اجرای دستی event loop
    loop = asyncio.get_event_loop()
    try:
        app = loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(app.shutdown())
        loop.close()
