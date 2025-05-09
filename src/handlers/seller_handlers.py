import logging
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
from sqlalchemy.orm import Session
from database.db import get_session
from database.models import Product
from utils.keyboards import get_seller_menu_keyboard, get_yes_no_keyboard
from constants import ROLE_SELLER
from typing import Dict, Any

# تنظیم لاگر
logger = logging.getLogger(__name__)

(
    ADD_PRODUCT, 
    SET_PRICE, 
    CONFIRM_PRODUCT, 
    DELETE_PRODUCT, 
    CONFIRM_DELETE,
    UPDATE_STOCK  # حالت جدید برای به‌روزرسانی موجودی
) = range(6)  # از 5 به 6 افزایش دهید

# هندلر منوی فروشنده
async def seller_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data.get("role") != ROLE_SELLER:
        await update.message.reply_text("⚠️ شما دسترسی به این منو ندارید!")
        return ConversationHandler.END

    try:
        keyboard = get_seller_menu_keyboard()
        await update.message.reply_text(
            "🛒 منوی فروشنده:",
            reply_markup=keyboard
        )
        return ADD_PRODUCT

    except Exception as e:
        logger.error(f"Error in seller_menu: {e}")
        await update.message.reply_text("⚠️ خطایی در نمایش منو رخ داد!")
        return ConversationHandler.END

# اضافه کردن محصول
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        product_name = update.message.text.strip()

        # اعتبارسنجی نام محصول
        if not product_name or len(product_name) > 100:
            await update.message.reply_text("⚠️ نام محصول نامعتبر است! (حداکثر 100 کاراکتر)")
            return ADD_PRODUCT

        context.user_data["new_product"] = {"name": product_name}
        await update.message.reply_text("💰 لطفاً قیمت محصول را به تومان وارد کنید:")
        return SET_PRICE

    except Exception as e:
        logger.error(f"Error in add_product: {e}")
        await update.message.reply_text("⚠️ خطایی در دریافت نام محصول رخ داد!")
        return ConversationHandler.END

# دریافت قیمت محصول
async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        price_text = update.message.text.strip()
        price = float(price_text)

        # اعتبارسنجی قیمت
        if price <= 0:
            await update.message.reply_text("⚠️ قیمت باید بیشتر از صفر باشد!")
            return SET_PRICE

        context.user_data["new_product"]["price"] = price
        keyboard = get_yes_no_keyboard()

        await update.message.reply_text(
            f"ℹ️ اطلاعات محصول:\n"
            f"📛 نام: {context.user_data['new_product']['name']}\n"
            f"💰 قیمت: {price:,} تومان\n\n"
            f"آیا تأیید می‌کنید؟",
            reply_markup=keyboard
        )
        return CONFIRM_PRODUCT

    except ValueError:
        await update.message.reply_text("⚠️ لطفاً یک عدد معتبر برای قیمت وارد کنید!")
        return SET_PRICE

    except Exception as e:
        logger.error(f"Error in set_price: {e}")
        await update.message.reply_text("⚠️ خطایی در دریافت قیمت رخ داد!")
        return ConversationHandler.END

# تایید محصول
async def confirm_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    try:
        if query.data == "yes":
            product_data = context.user_data["new_product"]

            with get_session() as session:
                existing_product = session.query(Product).filter(
                    Product.name == product_data["name"]
                ).first()

                if existing_product:
                    await query.edit_message_text(
                        text="⚠️ محصولی با این نام از قبل وجود دارد!",
                        reply_markup=None
                    )
                else:
                    new_product = Product(
                        name=product_data["name"],
                        price=product_data["price"]
                    )
                    session.add(new_product)
                    session.commit()

                    await query.edit_message_text(
                        text=f"✅ محصول '{product_data['name']}' با موفقیت اضافه شد!",
                        reply_markup=None
                    )
        else:
            await query.edit_message_text(
                text="❌ اضافه کردن محصول لغو شد.",
                reply_markup=None
            )

    except Exception as e:
        logger.error(f"Error in confirm_product: {e}")
        await query.edit_message_text(
            text="⚠️ خطایی در ثبت محصول رخ داد!",
            reply_markup=None
        )

    finally:
        if "new_product" in context.user_data:
            del context.user_data["new_product"]

    return ConversationHandler.END

# پردازش به‌روزرسانی موجودی
async def process_stock_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        product_name, stock_str = update.message.text.split(',')
        product_name = product_name.strip()
        stock = int(stock_str.strip())

        if stock < 0:
            await update.message.reply_text("⚠️ موجودی نمی‌تواند منفی باشد!")
            return UPDATE_STOCK

        with get_session() as session:
            product = session.query(Product).filter(
                Product.name == product_name
            ).first()

            if product:
                product.stock = stock
                session.commit()
                await update.message.reply_text(
                    f"✅ موجودی محصول '{product_name}' به {stock} عدد به‌روزرسانی شد."
                )
            else:
                await update.message.reply_text("⚠️ محصول یافت نشد!")

    except ValueError:
        await update.message.reply_text("⚠️ فرمت ورودی نامعتبر است!")
        return UPDATE_STOCK

    except Exception as e:
        logger.error(f"Error in process_stock_update: {e}")
        await update.message.reply_text("⚠️ خطایی در به‌روزرسانی موجودی رخ داد!")

    return ConversationHandler.END

# ثبت هندلرها
def register_handlers(app: Application) -> None:
    # مکالمه برای اضافه کردن محصول
    add_product_conv = ConversationHandler(
        entry_points=[CommandHandler("add_product", seller_menu)],
        states={
            ADD_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product)],
            SET_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_price)],
            CONFIRM_PRODUCT: [CallbackQueryHandler(confirm_product)],
            UPDATE_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_stock_update)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    # ثبت تمام هندلرها
    app.add_handler(add_product_conv)
    app.add_handler(CommandHandler("list_products", list_products))
    app.add_handler(CommandHandler("cancel", cancel))
