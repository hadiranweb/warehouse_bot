import os
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_TOKEN
from database import init_db
from handlers import start, add_item, list_items, delete_item

async def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("delete", delete_item))

    PORT = int(os.environ.get("PORT", 8000))  # Render پورت 8000
    RENDER_APP_NAME = os.environ.get("RENDER_APP_NAME")
    webhook_url = f"https://{RENDER_APP_NAME}.onrender.com/{TELEGRAM_TOKEN}"

    await app.bot.set_webhook(webhook_url)
    print(f"Webhook تنظیم شد: {webhook_url}")

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
