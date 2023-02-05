import requests
import time
from cred import bot_token, chat_id
from binance_functions import get_opened_positions, open_position, close_position

telegram_delay = 10     # time of working of the previous command from  telegram


def getTPSLfrom_telegram():
    """
    The function gets message from telegram and sends relevant commands to binance (open / close)

    :return: message from telegram (str)
    """
    # Getting text information from telegram
    strr = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(strr)
    rs = response.json()
    rs2 = rs['result'][-1]
    rs3 = rs2['message']
    textt = rs3['text']
    datet = rs3['date']

    # Subcycle to recognition of information from telegram
    if (time.time() - datet) < telegram_delay and textt in ('quit', 'exit', 'hello', 'open_short', 'open_long', 'close_pos'):
        return textt
    else:
        return None


def telegram_bot_sendtext(bot_message):
    """
    The function sends message to telegram

    :return: response information (json)
    """
    bot_token2 = bot_token
    bot_chatID = chat_id
    send_text = f"https://api.telegram.org/bot{bot_token2}/sendMessage?chat_id={bot_chatID}&parse_mode=Markdown&text={bot_message}"
    response = requests.get(send_text)
    return response.json()


