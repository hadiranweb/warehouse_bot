from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_menu(options):
    keyboard = [
        [InlineKeyboardButton(label, callback_data=action)]
        for label, action in options
    ]
    return InlineKeyboardMarkup(keyboard)

def role_selection_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("فروشنده", callback_data="role_seller"),
            InlineKeyboardButton("مشتری", callback_data="role_customer"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
