import logging
import asyncio
from config import BOT_TOKEN, WEBHOOK_URL, PORT  # افزودن صحیح متغیرهای گم‌شده
from telegram.ext import Application
from telegram.error import TelegramError
from database.db import init_db
from handlers.role_selection import register_handlers as register_role_handlers
from handlers.seller_handlers import register_handlers as register_seller_handlers
from handlers.customer_handlers import register_handlers as register_customer_handlers
from aiohttp import web

# تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# تابع async برای تشخیص
async def diagnostic():
    # شبیه‌سازی تابع تشخیص
    logger.info("در حال انجام تشخیص...")
    return True

# هندلر برای مسیر root (GET /)
async def handle_root(request):
    return web.Response(text="Server is up and running!")

# هندلر برای پردازش وب‌هوک
async def handle_webhook(request):
    try:
        update = await request.json()
        await request.app["bot_app"].process_update(update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error handling update: {e}")
        return web.Response(status=500)

# تابع اصلی
async def main():
    logger.info("🔍 شروع تشخیص...")
    if not await diagnostic():
        logger.error("تشخیص اولیه ناموفق بود!")
        return
    
    logger.info("✅ راه‌اندازی ربات...")
    
    # راه‌اندازی دیتابیس و ثبت هندلرها
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

    await app.initialize()
    await app.bot.set_webhook(full_webhook_url, secret_token="mysecret123")
    await app.start()

    # راه‌اندازی وب‌سرور برای وب‌هوک
    aiohttp_app = web.Application()
    aiohttp_app["bot_app"] = app
    aiohttp_app.router.add_post(webhook_path, handle_webhook)

    # افزودن هندلر برای root (GET /)
    aiohttp_app.router.add_get('/', handle_root)

    runner = web.AppRunner(aiohttp_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info(f"Webhook server started on port {PORT}")

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Shutdown initiated.")
    finally:
        await runner.cleanup()
        await app.stop()
        await app.shutdown()
        logger.info("Application and webhook server stopped successfully.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
    except Exception as e:
        logger.error(f"Application error: {e}")
