import asyncio
import logging
from telegram.ext import Application
from telegram.error import TelegramError
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from database.db import init_db
from handlers.role_selection import register_handlers as register_role_handlers
from handlers.seller_handlers import register_handlers as register_seller_handlers
from handlers.customer_handlers import register_handlers as register_customer_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ثبت هندلرها
    register_role_handlers(app)
    register_seller_handlers(app)
    register_customer_handlers(app)

    # تنظیم وب‌هوک
    webhook_path = f"/{BOT_TOKEN.replace(':', '_')}"
    full_webhook_url = f"{WEBHOOK_URL}{webhook_path}"
    logger.info(f"Setting webhook: {full_webhook_url}")

    try:
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=full_webhook_url,
        )
        logger.info("Webhook started successfully.")
    except TelegramError as e:
        logger.error(f"Failed to start webhook: {e}")
        raise

    return app

async def shutdown(app):
    if app is not None:
        logger.info("Stopping webhook...")
        try:
            await app.updater.stop()
            await app.stop()
            logger.info("Application stopped successfully.")
        except TelegramError as e:
            logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    # مقداردهی اولیه پایگاه داده
    init_db()

    loop = asyncio.get_event_loop()
    app = None
    try:
        app = loop.run_until_complete(main())
        loop.run_forever()
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        if app is not None:
            loop.run_until_complete(shutdown(app))
        loop.close()
        logger.info("Event loop closed.")
