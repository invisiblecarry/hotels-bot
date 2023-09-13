from telebot.types import Message, CallbackQuery
from database.core import crud
from database.common.models import db, RequestsHistory, ResultsHistory, RequestsResults
from loader import bot
from states.my_states import UserStates

db_write = crud.create() #
db_read = crud.retrive()


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:

    bot.send_message(message.from_user.id, 'Searching for your history...')
    result_1 = db_read(db, RequestsHistory, RequestsHistory, ResultsHistory)\
        .join(RequestsResults, on=(RequestsHistory.id == RequestsResults.request_id))\
        .join(ResultsHistory, on=(RequestsResults.result_id == ResultsHistory.id))\
        .where(RequestsHistory.user_id == message.from_user.id)
    for row in result_1:
        user_id = row.user_id
        command = row.command
        used_at = row.used_at
        searched = row.searched
        search_result = row.requestsresults.resultshistory.search_result
        address = row.requestsresults.resultshistory.address
        hotel_name = row.requestsresults.resultshistory.hotel_name
        hotel_id = row.requestsresults.resultshistory.hotel_id
        bot.send_message(message.from_user.id,
                         text=f"USER ID: {user_id}\nCOMMAND: {command}\nUSED AT: {used_at}\n"
                              f"SEARCHED: {searched}\nHOTELID: {hotel_id}\n"
                              f"HOTEL NAME: {hotel_name}\nADDRESS: {address}")
