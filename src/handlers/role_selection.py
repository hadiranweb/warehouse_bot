# src/handlers/role_selection.py
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)
from utils.keyboards import get_role_selection_keyboard
from constants import START_MESSAGE, ROLE_SELLER, ROLE_CUSTOMER

SELECT_ROLE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_role_selection_keyboard()
    await update.message.reply_text(START_MESSAGE, reply_markup=keyboard)
    return SELECT_ROLE

async def role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role = query.data
    if role in [ROLE_SELLER, ROLE_CUSTOMER]:
        context.user_data["role"] = role
        await query.message.reply_text(f"نقش شما به عنوان {role} تنظیم شد!")
        return ConversationHandler.END
    else:
        await query.message.reply_text("نقش نامعتبر! لطفاً دوباره انتخاب کنید.")
        return SELECT_ROLE

def register_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_ROLE: [CallbackQueryHandler(role_callback)],
        },
        fallbacks=[],
        per_message=True,
    )
    app.add_handler(conv_handler)
