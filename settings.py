from dotenv import *
import os

load_dotenv()

valid_email = os.getenv("EMAIL")
valid_password = os.getenv("PASS")

invalid_email = '48234@rambler.ru'
invalid_password = '1111111111'