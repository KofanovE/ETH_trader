import requests
import time
from cred import bot_token, chat_id
from binance_functions import get_opened_positions, open_position, close_position


global symbol, maxposition


telegram_delay = 13

def getTPSLfrom_telegram(symbol, maxposition):
    strr = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(strr)
    rs = response.json()
    rs2 = rs['result'][-1]
    rs3 = rs2['message']
    textt = rs3['text']
    datet = rs3['date']

    print(textt, "\n")
    print(time.time(), datet, time.time()-datet, telegram_delay)

    if (time.time() - datet) < telegram_delay:
        print("pic")
        if 'quit' in textt:
            quit()
        if 'exit' in textt:
            exit()
        if 'hello' in textt:
            telegram_bot_sendtext('Hello, how are you?')
        if 'open_short' in textt:
            print(symbol, maxposition)
            open_position(symbol, 'short', maxposition)
        if 'open_long' in textt:
            open_position(symbol, 'long', maxposition)
        if 'close_pos' in textt:
            position = get_opened_positions(symbol)
            open_sl = position[0]
            quantity = position[1]
            close_position(symbol, open_sl, abs(quantity))



def telegram_bot_sendtext(bot_message, symbol, maxposition):
    bot_token2 = bot_token
    bot_chatID = chat_id
    send_text = f"https://api.telegram.org/bot{bot_token2}/sendMessage?chat_id={bot_chatID}&parse_mode=Markdown&text={bot_message}"
    response = requests.get(send_text)
    return response.json()


    starttime = time.time()
    timeout = time.time() + 60*60*12
    counterr = 1

    while time.time() <= timeout:
        try:
            print("passthroug at "+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            getTPSLfrom_telegram(symbol, maxposition)
            time.sleep(15 - ((time.time() - starttime) % 15.0))
        except KeyboardInterrupt:
            print('\n\nKeyboard exception received. Exiting')
            exit()