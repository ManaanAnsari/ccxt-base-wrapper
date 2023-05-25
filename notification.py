import requests 
import os, certifi
import config as conf
os.environ['SSL_CERT_FILE'] = certifi.where()

def send_telegram_message(chat_ids=[],messages=[]):
    if conf.TELEGRAM_NOTIFICATION:
        url = 'https://api.telegram.org/bot'+conf.TELEGRAM_BOT_TOKEN+'/sendMessage' 
        if messages:
            for message in messages:
                if message:
                    for chat_id in chat_ids:
                        if chat_id:
                            payload = {'chat_id' : chat_id,'text' : message}
                            try:
                                res = requests.post(url,json=payload)
                            except Exception as e:
                                print(str(e))
                                return False
        return True
    else:
        print("TELEGRAM NOTIFICATION DISABLED")
        return False




# send_telegram_message(messages=["Hello World"])

