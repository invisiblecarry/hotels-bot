from telebot.handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    echo = State()
    search = State()
    region_id = State()
    results_size = State()
    minprice = State()
    maxprice = State()
    distance = State()
