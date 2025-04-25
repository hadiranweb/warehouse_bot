import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://warehouse-bot-123.onrender.com")
PORT = int(os.getenv("PORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "mysecret123")
