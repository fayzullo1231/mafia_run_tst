# from dotenv import load_dotenv, find_dotenv
# import os
#
# load_dotenv(find_dotenv())
# BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# BOT_USERNAME = os.getenv("BOT_USERNAME", "")  # 👈 .env'dan olinadi
#
# if not BOT_TOKEN or not BOT_USERNAME:
#     raise RuntimeError("BOT_TOKEN yoki BOT_USERNAME .env faylda mavjud emas!")

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # .env faylni yuklaydi
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME")

if not BOT_USERNAME:
    raise RuntimeError("BOT_USERNAME .env faylda yo'q yoki noto‘g‘ri yozilgan!")
