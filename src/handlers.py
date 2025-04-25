from telegram import Update
from telegram.ext import ContextTypes
from database import add_item_to_db, get_all_items, delete_item_from_db
from utils import validate_quantity

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("به ربات مدیریت انبار خوش آمدید!\nدستورات:\n/add <نام> <تعداد>\n/list\n/delete <id>")

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("لطفاً نام و تعداد را وارد کنید: /add <نام> <تعداد>")
            return
        name, quantity = args[0], args[1]
        quantity = validate_quantity(quantity)
        add_item_to_db(name, quantity)
        await update.message.reply_text(f"کالا '{name}' با تعداد {quantity} ثبت شد.")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        await update.message.reply_text(f"خطا: {str(e)}")

async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = get_all_items()
    if not items:
        await update.message.reply_text("انبار خالی است!")
        return
    response = "موجودی انبار:\n"
    for item in items:
        response += f"ID: {item[0]} | نام: {item[1]} | تعداد: {item[2]}\n"
    await update.message.reply_text(response)

async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("لطفاً ID کالا را وارد کنید: /delete <id>")
            return
        item_id = int(context.args[0])
        row_count = delete_item_from_db(item_id)
        if row_count == 0:
            await update.message.reply_text("کالا با این ID یافت نشد!")
        else:
            await update.message.reply_text(f"کالا با ID {item_id} حذف شد.")
    except ValueError:
        await update.message.reply_text("ID باید عدد باشد!")
    except Exception as e:
        await update.message.reply_text(f"خطا: {str(e)}")
