from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from api_requests.requests_to_api import api_request
from typing import Dict
import json


def markup(message: str) -> InlineKeyboardMarkup:
    cities = city_founding(message)
    if len(cities) >= 1:
        destinations = InlineKeyboardMarkup()
        for region_name, region_id in cities.items():
            destinations.add(InlineKeyboardButton(text=region_name,
                                                  callback_data=f'{region_id}rgID0'))

        return destinations


def city_founding(message: str) -> Dict:  # Функция city_founding -> словарь с нужными именем и id
    querystring = {"q": message}
    response_from_api = api_request(method_endswith='locations/v3/search',
                                    params=querystring,
                                    method_type='GET'
                                    )
    if response_from_api:
        result = json.loads(response_from_api.text)
        # city_list = filter(lambda loc: loc['type'] == 'CITY', result['sr'])
        cities = dict()
        for dest in result['sr']:  # Обрабатываем результат
            if dest['type'] == 'CITY':
                cities[dest['regionNames']['fullName']] = dest['essId']['sourceId']

        return cities
