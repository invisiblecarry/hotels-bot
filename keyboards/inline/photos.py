from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def markup(property_id: str) -> InlineKeyboardMarkup:
    code = 'prpID0'
    yes_no = InlineKeyboardMarkup()
    yes_no.add(InlineKeyboardButton(text='Open photos and details', callback_data=f'{property_id}{code}'))
    return yes_no
