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
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    register_role_handlers(app)
    register_seller_handlers(app)
    register_customer_handlers(app)
    webhook_path = f"/{BOT_TOKEN.replace(':', '_')}"
    full_webhook_url = f"{WEBHOOK_URL}{webhook_path}"
    if not full_webhook_url.startswith("https://"):
        logger.error(f"Invalid WEBHOOK_URL: {full_webhook_url}. Must use HTTPS.")
        raise ValueError("WEBHOOK_URL must use HTTPS")
    if ":" in WEBHOOK_URL.split("//")[1]:
        logger.error(f"WEBHOOK_URL contains invalid port: {WEBHOOK_URL}. Must use default HTTPS port (443).")
        raise ValueError("WEBHOOK_URL must not specify a port")
    logger.info(f"Setting webhook: {full_webhook_url}")
    try:
        await app.initialize()
        await app.bot.set_webhook(full_webhook_url, secret_token="mysecret123")
        await app.start()
        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            secret_token="mysecret123",
        )
        logger.info("Webhook started successfully.")
    except TelegramError as e:
        logger.error(f"Failed to start webhook: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        try:
            await app.stop()
            await app.shutdown()
            logger.info("Application stopped successfully.")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Application error: {e}")
