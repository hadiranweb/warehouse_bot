from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)
from utils.keyboards import create_menu
from constants import CUSTOMER_MENU

VIEW_CREDIT_PURCHASES = 0

async def view_credit_purchases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # اینجا باید داده‌های خریدهای اعتباری از پایگاه داده خوانده شود
    await query.message.reply_text("لیست خریدهای اعتباری شما: (نمونه)")
    await query.message.reply_text("بازگشت به داشبورد:", reply_markup=create_menu(CUSTOMER_MENU))
    return ConversationHandler.END

def register_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(view_credit_purchases, pattern="^view_credit_purchases$")],
        states={VIEW_CREDIT_PURCHASES: []},
        fallbacks=[],
    )
    app.add_handler(conv_handler)
