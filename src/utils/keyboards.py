from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from constants import ROLE_SELLER, ROLE_CUSTOMER

def get_role_selection_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("فروشنده", callback_data=ROLE_SELLER),
            InlineKeyboardButton("مشتری", callback_data=ROLE_CUSTOMER),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_yes_no_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("بله", callback_data="yes"),
            InlineKeyboardButton("خیر", callback_data="no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
