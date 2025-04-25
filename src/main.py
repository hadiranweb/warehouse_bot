import logging
import asyncio
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
    # مقداردهی اولیه پایگاه داده
    init_db()

    # ساخت Application
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
        # تنظیم وب‌هوک
        await app.bot.set_webhook(full_webhook_url, secret_token="mysecret123")  # توکن امن
        # اجرای اپلیکیشن با وب‌هوک
        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=full_webhook_url,
            secret_token="mysecret123",  # باید با set_webhook یکسان باشد
        )
        logger.info("Webhook started successfully.")
    except TelegramError as e:
        logger.error(f"Failed to start webhook: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Application error: {e}")
