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



run_data = {
    "4h": {
        "BTC/USDT": {
            "SampleStrategy": {
                "custom": [
                    {
                        "exchange": "binance",
                        "exchange_params": {
                            "API_KEY": "your api key",
                            "API_KEY_SECRET": "your api key secret",
                            "PASSWORD": None,
                            "TESTNET": True,
                            "telegram_chat_id": None # your telegram chat id
                        },
                        "strategy_params": {
                            "risk_perc": 0.1, #risk oinly 10% of your portfolio
                            "sl_perc": 0.02, # stop loss 2%
                            "leverage": 3, # leverage 3x
                            "tpsl_buffer_perc": 0.03 # take profit and stop loss buffer 3%
                        }
                    },
                    {
                        "exchange": "bitmex",
                        "exchange_params": {
                            "API_KEY": "your api key",
                            "API_KEY_SECRET": "your api key secret",
                            "PASSWORD": None,
                            "TESTNET": True,
                            "telegram_chat_id": None # your telegram chat id
                        },
                        "strategy_params": {
                            "risk_perc": 0.1,
                            "sl_perc": 0.02,
                            "leverage": 3,
                            "tpsl_buffer_perc": 0.03
                        }
                    }
                ]
            }
        },
        "ETH/USDT": {
            "SampleStrategy": {
                "custom": [
                    {
                        "exchange": "binance",
                        "exchange_params": {
                            "API_KEY": "your api key",
                            "API_KEY_SECRET": "your api key secret",
                            "PASSWORD": None,
                            "TESTNET": True,
                            "telegram_chat_id": None # your telegram chat id
                        },
                        "strategy_params": {
                            "risk_perc": 0.1, #risk oinly 10% of your portfolio
                            "sl_perc": 0.02, # stop loss 2%
                            "leverage": 3, # leverage 3x
                            "tpsl_buffer_perc": 0.03 # take profit and stop loss buffer 3%
                        }
                    },
                    {
                        "exchange": "bitmex",
                        "exchange_params": {
                            "API_KEY": "your api key",
                            "API_KEY_SECRET": "your api key secret",
                            "PASSWORD": None,
                            "TESTNET": True,
                            "telegram_chat_id": None # your telegram chat id
                        },
                        "strategy_params": {
                            "risk_perc": 0.1,
                            "sl_perc": 0.02,
                            "leverage": 3,
                            "tpsl_buffer_perc": 0.03
                        }
                    }
                ]
            }
        }
    }
}

