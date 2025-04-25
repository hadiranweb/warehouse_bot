import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# بارگذاری توکن از .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# راه‌اندازی دیتابیس SQLite
def init_db():
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )""")
    conn.commit()
    conn.close()

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("به ربات مدیریت انبار خوش آمدید!\nدستورات:\n/add <نام> <تعداد>\n/list\n/delete <id>")

# دستور /add برای ثبت کالای جدید
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("لطفاً نام و تعداد را وارد کنید: /add <نام> <تعداد>")
            return
        name, quantity = args[0], args[1]
        quantity = int(quantity)
        if quantity <= 0:
            await update.message.reply_text("تعداد باید مثبت باشد!")
            return

        conn = sqlite3.connect("warehouse.db")
        c = conn.cursor()
        c.execute("INSERT INTO items (name, quantity) VALUES (?, ?)", (name, quantity))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"کالا '{name}' با تعداد {quantity} ثبت شد.")
    except ValueError:
        await update.message.reply_text("تعداد باید عدد باشد!")
    except Exception as e:
        await update.message.reply_text(f"خطا: {str(e)}")

# دستور /list برای نمایش موجودی
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("SELECT id, name, quantity FROM items")
    items = c.fetchall()
    conn.close()

    if not items:
        await update.message.reply_text("انبار خالی است!")
        return

    response = "موجودی انبار:\n"
    for item in items:
        response += f"ID: {item[0]} | نام: {item[1]} | تعداد: {item[2]}\n"
    await update.message.reply_text(response)

# دستور /delete برای حذف کالا
async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("لطفاً ID کالا را وارد کنید: /delete <id>")
            return
        item_id = int(context.args[0])

        conn = sqlite3.connect("warehouse.db")
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE id = ?", (item_id,))
        if c.rowcount == 0:
            await update.message.reply_text("کالا با این ID یافت نشد!")
        else:
            conn.commit()
            await update.message.reply_text(f"کالا با ID {item_id} حذف شد.")
        conn.close()
    except ValueError:
        await update.message.reply_text("ID باید عدد باشد!")
    except Exception as e:
        await update.message.reply_text(f"خطا: {str(e)}")

# تابع اصلی برای راه‌اندازی ربات
def main():
    init_db()  # راه‌اندازی دیتابیس
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ثبت دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("delete", delete_item))

    # شروع ربات
    print("ربات در حال اجرا است...")
    app.run_polling()

if __name__ == "__main__":
    main()
