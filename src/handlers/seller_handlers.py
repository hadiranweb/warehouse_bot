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
from utils.keyboards import get_seller_menu_keyboard, get_yes_no_keyboard
from constants import ROLE_SELLER

ADD_PRODUCT, SET_PRICE, CONFIRM_PRODUCT, DELETE_PRODUCT, CONFIRM_DELETE = range(5)

async def seller_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("role") != ROLE_SELLER:
        await update.message.reply_text("شما دسترسی به این منو ندارید!")
        return ConversationHandler.END
    keyboard = get_seller_menu_keyboard()
    await update.message.reply_text("منوی فروشنده:", reply_markup=keyboard)
    return ADD_PRODUCT

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_product"] = {"name": update.message.text}
    await update.message.reply_text("لطفاً قیمت محصول را وارد کنید:")
    return SET_PRICE

async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text)
        context.user_data["new_product"]["price"] = price
        keyboard = get_yes_no_keyboard()
        await update.message.reply_text(
            f"محصول: {context.user_data['new_product']['name']}, قیمت: {price}\nتأیید می‌کنید؟",
            reply_markup=keyboard,
        )
        return CONFIRM_PRODUCT
    except ValueError:
        await update.message.reply_text("لطفاً یک عدد معتبر برای قیمت وارد کنید!")
        return SET_PRICE

async def confirm_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "yes":
        with get_session() as session:
            product = Product(
                name=context.user_data["new_product"]["name"],
                price=context.user_data["new_product"]["price"],
            )
            session.add(product)
            session.commit()
        await query.message.reply_text("محصول با موفقیت اضافه شد!")
    else:
        await query.message.reply_text("اضافه کردن محصول لغو شد.")
    return ConversationHandler.END

async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text
    with get_session() as session:
        product = session.query(Product).filter(Product.name == product_name).first()
        if product:
            context.user_data["delete_product_id"] = product.id
            keyboard = get_yes_no_keyboard()
            await update.message.reply_text(
                f"آیا مطمئن هستید که می‌خواهید '{product_name}' را حذف کنید؟",
                reply_markup=keyboard,
            )
            return CONFIRM_DELETE
        else:
            await update.message.reply_text("محصول یافت نشد!")
            return ConversationHandler.END

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "yes":
        with get_session() as session:
            product = session.query(Product).filter(
                Product.id == context.user_data["delete_product_id"]
            ).first()
            if product:
                session.delete(product)
                session.commit()
                await query.message.reply_text("محصول با موفقیت حذف شد!")
            else:
                await query.message.reply_text("محصول یافت نشد!")
    else:
        await query.message.reply_text("حذف محصول لغو شد.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

def register_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", seller_menu, filters=filters.User(user_id=None, allow_empty=True))],
        states={
            ADD_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product)],
            SET_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_price)],
            CONFIRM_PRODUCT: [CallbackQueryHandler(confirm_product)],
            DELETE_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_product)],
            CONFIRM_DELETE: [CallbackQueryHandler(confirm_delete)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )
    app.add_handler(conv_handler)
