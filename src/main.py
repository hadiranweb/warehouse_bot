import logging
import asyncio
from telegram.ext import Application
from telegram.error import TelegramError
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from database.db import init_db
from handlers.role_selection import register_handlers as register_role_handlers
from handlers.seller_handlers import register_handlers as register_seller_handlers
from handlers.customer_handlers import register_handlers as register_customer_handlers

from aiohttp import web

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def handle_webhook(request):
    try:
        update = await request.json()
        logger.info(f"Received update: {update}")
        await request.app["bot_app"].process_update(update)
        return web.json_response({"status": "ok", "message": "update processed"})
    except Exception as e:
        logger.exception("Error handling update")
        return web.json_response({"status": "error", "message": str(e)}, status=500)
        
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

    await app.initialize()
    await app.bot.set_webhook(full_webhook_url, secret_token="mysecret123")
    await app.start()

    aiohttp_app = web.Application()
    aiohttp_app["bot_app"] = app
    aiohttp_app.router.add_post(webhook_path, handle_webhook)

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
