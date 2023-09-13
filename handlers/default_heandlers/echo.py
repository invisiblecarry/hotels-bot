from telebot.types import Message
from states.my_states import UserStates
from loader import bot


@bot.message_handler(commands=['echo'])
def bot_echo(message: Message):
    bot.send_message(message.from_user.id, 'Echo mode started, write something')
    bot.set_state(user_id=message.from_user.id, state=UserStates.echo)


@bot.message_handler(state=UserStates.echo)
def echo_mode(message: Message):
    bot.reply_to(message, f"Echo {message.text}")
