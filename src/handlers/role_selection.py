from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from constants import ROLE_SELLER, ROLE_CUSTOMER, START_MESSAGE
from utils.keyboards import get_role_selection_keyboard
from typing import Dict, Any

# حالت‌های مکالمه
SELECTING_ROLE = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع مکالمه و انتخاب نقش"""
    try:
        await update.message.reply_text(
            START_MESSAGE,
            reply_markup=get_role_selection_keyboard()
        )
        return SELECTING_ROLE
    
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await update.message.reply_text("⚠️ خطایی در شروع ربات رخ داد!")
        return ConversationHandler.END

async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پردازش انتخاب نقش"""
    query = update.callback_query
    await query.answer()
    
    try:
        role = query.data
        context.user_data["role"] = role
        
        if role == ROLE_SELLER:
            message = "👨‍💼 شما به عنوان فروشنده وارد شدید. از منوی فروشنده استفاده کنید."
        else:
            message = "👤 شما به عنوان مشتری وارد شدید. از منوی مشتری استفاده کنید."
        
        await query.edit_message_text(text=message)
        return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in select_role: {e}")
        await query.edit_message_text(text="⚠️ خطایی در انتخاب نقش رخ داد!")
        return ConversationHandler.END

def register_handlers(app: Application) -> None:
    """ثبت هندلرهای انتخاب نقش"""
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ROLE: [
                CallbackQueryHandler(
                    select_role, 
                    pattern=f"^{ROLE_SELLER}$|^{ROLE_CUSTOMER}$"
                )
            ],
        },
        fallbacks=[],
        per_message=True,  # برای مدیریت بهتر callback queries
    )
    
    app.add_handler(conv_handler)
