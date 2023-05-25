from dotenv import load_dotenv
import os
from helper import *
load_dotenv()
import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(level=logging.INFO,filename='app.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s')


TELEGRAM_NOTIFICATION = strToBool(os.getenv("TELEGRAM_NOTIFICATION"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
