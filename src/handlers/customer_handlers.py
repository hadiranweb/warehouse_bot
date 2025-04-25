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
from constants import ROLE_CUSTOMER
from typing import Dict, Any, Optional

# حالت‌های مکالمه
VIEW_PRODUCTS, BUY_PRODUCT = range(2)

async def customer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """منوی اصلی مشتری"""
    if context.user_data.get("role") != ROLE_CUSTOMER:
        await update.message.reply_text("شما دسترسی به این منو ندارید!")
        return ConversationHandler.END
    
    try:
        with get_session() as session:
            products = session.query(Product).all()
            if products:
                message = "محصولات موجود:\n" + "\n".join(
                    [f"{idx+1}. {p.name} - قیمت: {p.price} تومان" for idx, p in enumerate(products)]
                )
                context.user_data["products"] = [p.name for p in products]
            else:
                message = "⚠️ هیچ محصولی موجود نیست."
                
        await update.message.reply_text(message)
        return VIEW_PRODUCTS
    
    except Exception as e:
        logger.error(f"Error in customer_menu: {e}")
        await update.message.reply_text("خطایی در دریافت محصولات رخ داد!")
        return ConversationHandler.END

async def view_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """نمایش محصولات و درخواست انتخاب"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="لطفاً شماره محصول مورد نظر را وارد کنید:",
        reply_markup=None
    )
    return BUY_PRODUCT

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پردازش خرید محصول"""
    try:
        product_idx = int(update.message.text) - 1
        products = context.user_data.get("products", [])
        
        if 0 <= product_idx < len(products):
            product_name = products[product_idx]
            
            with get_session() as session:
                product = session.query(Product).filter(Product.name == product_name).first()
                if product:
                    # در اینجا منطق خرید را پیاده‌سازی کنید
                    await update.message.reply_text(
                        f"✅ شما محصول '{product_name}' را با موفقیت خریداری کردید!\n"
                        f"💰 قیمت: {product.price} تومان"
                    )
                else:
                    await update.message.reply_text("⚠️ محصول مورد نظر یافت نشد!")
        else:
            await update.message.reply_text("⚠️ شماره محصول نامعتبر است!")
    
    except ValueError:
        await update.message.reply_text("⚠️ لطفاً فقط عدد وارد کنید!")
        return BUY_PRODUCT
    
    except Exception as e:
        logger.error(f"Error in buy_product: {e}")
        await update.message.reply_text("⚠️ خطایی در پردازش خرید رخ داد!")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو مکالمه"""
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

def register_handlers(app: Application) -> None:
    """ثبت هندلرهای مشتری"""
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("customer", customer_menu)],
        states={
            VIEW_PRODUCTS: [CallbackQueryHandler(view_products)],
            BUY_PRODUCT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, buy_product)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,  # برای مدیریت بهتر مکالمات
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("cancel", cancel))
