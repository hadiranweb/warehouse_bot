from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from constants import ROLE_SELLER, ROLE_CUSTOMER, START_MESSAGE
from utils.keyboards import get_role_selection_keyboard  # ایمپورت تابع درست

SELECTING_ROLE = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        START_MESSAGE, reply_markup=get_role_selection_keyboard()
    )
    return SELECTING_ROLE

async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    role = query.data
    context.user_data["role"] = role
    await query.message.reply_text(f"You selected {role}")
    return ConversationHandler.END

def register_handlers(app: Application) -> None:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ROLE: [
                CallbackQueryHandler(select_role, pattern=f"^{ROLE_SELLER}$|^{ROLE_CUSTOMER}$"),
            ],
        },
        fallbacks=[],
        per_message=True,
    )
    app.add_handler(conv_handler)
