from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)
from constants import START_MESSAGE, ROLE_SELLER, ROLE_CUSTOMER
from utils.keyboards import role_selection_keyboard
from database.db import get_session
from database.models import User, Role

SELECT_ROLE = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_MESSAGE, reply_markup=role_selection_keyboard())
    return SELECT_ROLE

async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id
    role = Role.SELLER if query.data == "role_seller" else Role.CUSTOMER

    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, role=role, name=query.from_user.first_name)
            session.add(user)
            session.commit()

    await query.message.reply_text(f"نقش شما: {ROLE_SELLER if role == Role.SELLER else ROLE_CUSTOMER}")
    await query.message.reply_text(
        "به داشبورد خود خوش آمدید!",
        reply_markup=create_menu(
            constants.SELLER_MENU if role == Role.SELLER else constants.CUSTOMER_MENU
        ),
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

def register_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={SELECT_ROLE: [CallbackQueryHandler(select_role, pattern="^role_.*")]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
