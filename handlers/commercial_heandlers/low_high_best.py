import json
from datetime import datetime, date
from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from database.core import *
from database.common.models import db, RequestsHistory, ResultsHistory, RequestsResults
from api_requests.requests_to_api import api_request
from keyboards.inline import cities, results_size, photos
from loader import bot
from states.my_states import UserStates

db_write = crud.create()
db_read = crud.retrive()


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def lowhighprice(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Enter the city..')
    bot.set_state(message.from_user.id, UserStates.search, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['datetime'] = datetime.utcnow()
        data['command'] = message.text[1:]


@bot.message_handler(state=UserStates.search)
def search_city(message: Message) -> None:
    bot.send_message(message.from_user.id,
                     'Please clarify destination:',
                     reply_markup=cities.markup(message.text)
                     )
    bot.set_state(message.from_user.id, UserStates.region_id, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['search'] = message.text
        data_to_record = {'user_id': message.from_user.id, "command": data['command'],
                          'used_at': data['datetime'], "searched": data['search']}
        rq_history = db_write(db, RequestsHistory, **data_to_record)
        data['rq_id'] = rq_history.id


@bot.callback_query_handler(state=UserStates.region_id, func=lambda call: call.data.endswith('rgID0'))
def region_id_check(call: CallbackQuery) -> None:
    bot.set_state(user_id=call.from_user.id, state=UserStates.results_size, chat_id=call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['region_id'] = call.data[:-5]

    bot.answer_callback_query(callback_query_id=call.id, text='Thank you!')
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Set results size',
                          reply_markup=results_size.markup())


@bot.callback_query_handler(state=UserStates.results_size, func=lambda call: call.data.endswith('rsz0'))
def result_size_check(call: CallbackQuery) -> None:
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['results_size'] = call.data[:-4]
    bot.answer_callback_query(callback_query_id=call.id, text='Thank you!')
    calendar, step = DetailedTelegramCalendar(calendar_id=0, min_date=date.today()).build()
    bot.edit_message_text(f"Select {LSTEP[step]}",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=0))
def check_in_check(call: CallbackQuery) -> None:
    result, key, step = DetailedTelegramCalendar(calendar_id=0).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Your check-in date {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check-in'] = result
        calendar, step2 = DetailedTelegramCalendar(calendar_id=1, min_date=result).build()
        bot.send_message(call.message.chat.id,
                         text=f"Select {LSTEP[step]}",
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def check_out_check(call: CallbackQuery) -> None:
    result, key, step = DetailedTelegramCalendar(calendar_id=1).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Your check-out date {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check-out'] = result
            if data['command'] == 'lowprice':
                sort = "PRICE_LOW_TO_HIGH"
            elif data['command'] == 'highprice':
                sort = "PRICE_HIGH_TO_LOW"
            elif data['command'] == 'bestdeal':
                sort = "DISTANCE"
            res_size = data['results_size']
            regionId = data['region_id']
            year_in, month_in, day_in = f'{data["check-in"]}'.split('-')
            year_out, month_out, day_out = f'{data["check-out"]}'.split('-')
            data['params'] = {
                "destination": {
                    "regionId": regionId
                },
                "checkInDate": {
                    "day": int(day_in),
                    "month": int(month_in),
                    "year": int(year_in)
                },
                "checkOutDate": {
                    "day": int(day_out),
                    "month": int(month_out),
                    "year": int(year_out)
                },
                'rooms': [{'adults': 2}],
                "resultsSize": int(res_size),
                "sort": sort,
                'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}

            }
        if sort == 'DISTANCE':
            bot.set_state(call.from_user.id, UserStates.minprice, call.message.chat.id)
            bot.send_message(call.message.chat.id, text=f"Set min price(USD)...")

        else:

            response = api_request(method_endswith='properties/v2/list',
                                   params=data['params'],
                                   method_type='POST'
                                   )
            info = json.loads(response.text)
            hotels = ''
            for i_prop in info['data']['propertySearch']['properties']:
                name, neigd, price = 'empty', 'empty', 'empty'
                if 'name' in i_prop:
                    name = i_prop.get('name')
                    data['hotel_name'] = name
                    hotels += name + '\n'
                    data['hotels'] = hotels
                if 'neighborhood' in i_prop and i_prop['neighborhood'] is not None:
                    neigd = i_prop['neighborhood'].get('name')
                if 'price' in i_prop:
                    if 'lead' in i_prop['price']:
                        amount = round(i_prop['price']['lead'].get('amount'), 2)
                        price = f"{amount}$"
                bot.send_message(call.message.chat.id, text='Name: {name}\n\n'
                                                            'Neighborhood: {neigd}\n\n'
                                                            'Price per night: {price}'.format(name=f'"{name}"',
                                                                                              neigd=neigd,
                                                                                              price=price
                                                                                              ),
                                 reply_markup=photos.markup(i_prop.get('id'))
                                 )


# @bot.message_handler(state=UserStates.final)
# def prorepties_result(message: Message) -> None:
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         if data['command'] == 'lowprice':
#             sort = "PRICE_LOW_TO_HIGH"
#         elif data['command'] == 'highprice':
#             sort = "PRICE_HIGH_TO_LOW"
#         elif data['command'] == 'bestdeal':
#             sort = "DISTANCE"
#         res_size = data['results_size']
#         regionId = data['region_id']
#         year_in, month_in, day_in = f'{data["check-in"]}'.split('-')
#         year_out, month_out, day_out = f'{data["check-out"]}'.split('-')
#         params = {
#             "destination": {
#                 "regionId": regionId
#             },
#             "checkInDate": {
#                 "day": int(day_in),
#                 "month": int(month_in),
#                 "year": int(year_in)
#             },
#             "checkOutDate": {
#                 "day": int(day_out),
#                 "month": int(month_out),
#                 "year": int(year_out)
#             },
#             'rooms': [{'adults': int(message.text)}],
#             "resultsSize": int(res_size),
#             "sort": sort,
#             'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
#
#         }
#         if sort == 'DISTANCE':
#             bot.
#         else:
#
#             response = api_request(method_endswith='properties/v2/list',
#                                    params=params,
#                                    method_type='POST'
#                                    )
#             info = json.loads(response.text)
#             hotels = ''
#
#             for i_prop in info['data']['propertySearch']['properties']:
#                 name, neigd, price = 'empty', 'empty', 'empty'
#                 if 'name' in i_prop:
#                     name = i_prop.get('name')
#                     data['hotel_name'] = name
#                     hotels += name + '\n'
#                     data['hotels'] = hotels
#                 if 'neighborhood' in i_prop and i_prop['neighborhood'] is not None:
#                     neigd = i_prop['neighborhood'].get('name')
#                 if 'price' in i_prop:
#                     if 'lead' in i_prop['price']:
#                         amount = round(i_prop['price']['lead'].get('amount'), 2)
#                         price = f"{amount}$"
#                 bot.send_message(message.chat.id, text='Name: {name}\n\n'
#                                                        'Neighborhood: {neigd}\n\n'
#                                                        'Price per night: {price}'.format(name=f'"{name}"',
#                                                                                          neigd=neigd,
#                                                                                          price=price
#                                                                                          ),
#                                  reply_markup=photos.markup(i_prop.get('id'))
#                                  )
@bot.message_handler(state=UserStates.minprice)
def minprice(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_price'] = message.text
    bot.set_state(message.from_user.id, UserStates.maxprice, message.chat.id)
    bot.send_message(message.chat.id, text=f"Set max price(USD)...")


@bot.message_handler(state=UserStates.maxprice)
def maxprice(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['max_price'] = message.text
    bot.set_state(message.from_user.id, UserStates.distance, message.chat.id)
    bot.send_message(message.chat.id, text=f"Max distance from center...")


@bot.message_handler(state=UserStates.distance)
def distance(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['distance'] = message.text
        params = data['params']
        params['filters']['price'] = {
            "max": int(data['max_price']),
            "min": int(data['min_price'])
        }
        print(params)
        response = api_request(method_endswith='properties/v2/list',
                               params=params,
                               method_type='POST'
                               )
        info = json.loads(response.text)
        hotels = []
        for i_prop in info['data']['propertySearch']['properties']:
            if i_prop['destinationInfo']['distanceFromDestination']['value'] <= int(data['distance']):
                name, neigd, price = 'empty', 'empty', 'empty'
                if 'name' in i_prop:
                    name = i_prop.get('name')
                    data['hotel_name'] = name
                    hotels.append(name)
                    data['hotels'] = hotels
                    if 'neighborhood' in i_prop and i_prop['neighborhood'] is not None:
                        neigd = i_prop['neighborhood'].get('name')
                    if 'price' in i_prop:
                        if 'lead' in i_prop['price']:
                            amount = round(i_prop['price']['lead'].get('amount'), 2)
                            price = f"{amount}$"
                bot.send_message(message.chat.id, text='Name: {name}\n\n'
                                                       'Neighborhood: {neigd}\n\n'
                                                       'Price per night: {price}'.format(name=f'"{name}"',
                                                                                         neigd=neigd,
                                                                                         price=price
                                                                                         ),
                                 reply_markup=photos.markup(i_prop.get('id'))
                                 )


@bot.callback_query_handler(func=lambda call: call.data.endswith('prpID0'))
def photos_output(call: CallbackQuery) -> None:
    """
    Cllback Query handler.
    catches a callback data with property ID
    makes a request to the 'properties/v2/detail' endpoint with it
    receives a response, pulls out links to images and shows them in the same message where the button was clicked
    :arg call - CallbackQuery
    :return None
    """

    bot.answer_callback_query(callback_query_id=call.id, text='Thank you!')
    params = {"propertyId": call.data[:-6]}
    response = api_request(method_endswith='properties/v2/detail',
                           params=params,
                           method_type='POST'
                           )
    info = json.loads(response.text)
    pictures_url_list = [img['image']['url'] for img in info['data']['propertyInfo']['propertyGallery']['images']]
    urls = str()
    # coordinates = f"{info['data']['propertyInfo']['summary']['location']['coordinates']['latitude']} " \
    #               f"{info['data']['propertyInfo']['summary']['location']['coordinates']['longitude']}"
    address = info['data']['propertyInfo']['summary']['location']['address']['addressLine']
    hotel_info = call.message.text
    for index, value in enumerate(pictures_url_list):
        urls += f'{index + 1}. {value}\n\n'
        if index == 24:
            break
    bot.edit_message_text(f"{hotel_info}\n\n"
                          f"Description: {info['data']['propertyInfo']['summary']['tagline']}\n"
                          f"Address: {address}\n\n"
                          # f"Geolocation: {coordinates}\n\n"
                          f"Photos: \n{urls}",
                          call.message.chat.id,
                          call.message.message_id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data_to_record = {'search_result': data['hotels'], 'hotel_id': int(params['propertyId']),
                          'hotel_name': data['hotel_name'], 'address': address,
                          'photo_links': urls}
        res_history = db_write(db, ResultsHistory, **data_to_record)
        res_id = res_history.id

        data_to_record = {'request_id': data['rq_id'], 'result_id': res_id}
        db_write(db, RequestsResults, **data_to_record)
