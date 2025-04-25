import os
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from config import TELEGRAM_TOKEN
from database import init_db
from handlers import start, add_item, list_items, delete_item
import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException

# تنظیم FastAPI
app = FastAPI()

async def webhook(update: dict):
    """مدیریت آپدیت‌های تلگرام"""
    telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("add", add_item))
    telegram_app.add_handler(CommandHandler("list", list_items))
    telegram_app.add_handler(CommandHandler("delete", delete_item))
    
    update_obj = Update.de_json(update, telegram_app.bot)
    await telegram_app.process_update(update_obj)
    return {"status": "ok"}

@app.post("/{token}")
async def telegram_webhook(token: str, request: Request):
    """دریافت درخواست‌های webhook"""
    if token != TELEGRAM_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    update = await request.json()
    await webhook(update)
    return {"status": "ok"}

async def set_webhook():
    """تنظیم webhook در هنگام شروع"""
    init_db()
    RENDER_APP_NAME = os.environ.get("RENDER_APP_NAME")
    webhook_url = f"https://{RENDER_APP_NAME}.onrender.com/{TELEGRAM_TOKEN}"
    telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
    await telegram_app.bot.set_webhook(webhook_url)
    print(f"Webhook تنظیم شد: {webhook_url}")

if __name__ == "__main__":
    # اجرای سرور با uvicorn
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    PORT = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
