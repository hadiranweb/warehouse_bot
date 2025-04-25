# src/handlers/customer_handlers.py
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from database.db import get_session
from database.models import Product
from constants import ROLE_CUSTOMER

VIEW_PRODUCTS, BUY_PRODUCT = range(2)

async def customer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("role") != ROLE_CUSTOMER:
        await update.message.reply_text("شما دسترسی به این منو ندارید!")
        return ConversationHandler.END
    with get_session() as session:
        products = session.query(Product).all()
        if products:
            message = "محصولات موجود:\n" + "\n".join(
                [f"{p.name}: {p.price}" for p in products]
            )
        else:
            message = "هیچ محصولی موجود نیست."
    await update.message.reply_text(message)
    return VIEW_PRODUCTS

async def view_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("لطفاً نام محصول مورد نظر را وارد کنید:")
    return BUY_PRODUCT

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text
    with get_session() as session:
        product = session.query(Product).filter(Product.name == product_name).first()
        if product:
            await update.message.reply_text(f"شما '{product_name}' را خریداری کردید!")
        else:
            await update.message.reply_text("محصول یافت نشد!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

def register_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", customer_menu)],
        states={
            VIEW_PRODUCTS: [CallbackQueryHandler(view_products)],
            BUY_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_product)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )
    app.add_handler(conv_handler)
