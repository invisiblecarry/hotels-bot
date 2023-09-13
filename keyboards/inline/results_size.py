from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def markup() -> InlineKeyboardMarkup:
    code = 'rsz0'
    nums = InlineKeyboardMarkup()
    nums.add(InlineKeyboardButton(text='10 hotels', callback_data=f'10{code}'))
    nums.add(InlineKeyboardButton(text='20 hotels', callback_data=f'20{code}'))
    nums.add(InlineKeyboardButton(text='50 hotels', callback_data=f'50{code}'))
    nums.add(InlineKeyboardButton(text='100 hotels', callback_data=f'100{code}'))
    nums.add(InlineKeyboardButton(text='150 hotels', callback_data=f'150{code}'))
    nums.add(InlineKeyboardButton(text='200 hotels', callback_data=f'200{code}'))

    return nums
