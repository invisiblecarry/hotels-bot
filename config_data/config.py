import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Environment variables not loaded because file is missing .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Start bot"),
    ('help', "Display help"),
    ('echo', "Echo mode"),
    ('lowprice', "Search hotels by price ascending"),
    ('highprice', "Search hotels by price descending"),
    ('bestdeal', "Search hotels that are most suitable for price and distance from center")
)
