from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from utils.keyboards import create_menu
from database.db import get_session
from database.models import User
from constants import SELLER_MENU

CUSTOMER_MANAGEMENT, ADD_CUSTOMER, SAVE_CUSTOMER = range(3)

async def customer_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    menu = [
        ("ثبت مشتری جدید", "add_customer"),
        ("حذف مشتری", "delete_customer"),
        ("اصلاح اطلاعات مشتری", "edit_customer"),
        ("جستجوی مشتری", "search_customer"),
        ("لیست مشتریان", "list_customers"),
    ]
    await query.message.reply_text("مدیریت مشتریان:", reply_markup=create_menu(menu))
    return CUSTOMER_MANAGEMENT

async def add_customer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("لطفاً اطلاعات مشتری را وارد کنید (نام، شماره تماس، آدرس (اختیاری)، ایمیل (اختیاری)):")
    return ADD_CUSTOMER

async def save_customer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split(",")
    name = text[0].strip()
    phone = text[1].strip() if len(text) > 1 else None
    address = text[2].strip() if len(text) > 2 else None
    email = text[3].strip() if len(text) > 3 else None

    with get_session() as session:
        customer = User(name=name, phone=phone, address=address, email=email, role="customer")
        session.add(customer)
        session.commit()

    await update.message.reply_text("مشتری با موفقیت ثبت شد.", reply_markup=create_menu(SELLER_MENU))
    return ConversationHandler.END

def register_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(customer_management, pattern="^customer_management$")],
        states={
            CUSTOMER_MANAGEMENT: [CallbackQueryHandler(add_customer, pattern="^add_customer$")],
            ADD_CUSTOMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_customer)],
        },
        fallbacks=[],
        per_message=True,
    )
    app.add_handler(conv_handler)
