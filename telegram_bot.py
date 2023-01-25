import requests
import time
from cred import bot_token, chat_id




telegram_delay = 8

def getTPSLfrom_telegram():
    strr = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(strr)
    rs = response.json()
    rs2 = rs['result'][-1]
    rs3 = rs2['message']
    textt = rs3['text']
    datet = rs3['date']

    if (time.time() - datet) < telegram_delay:
        if 'quit' in textt:
            quit()
        if 'exit' in textt:
            exit()
        if 'hello' in textt:
            telegram_bot sendtext('Hello, how are you?')
        if 'close_pos' in textt:
            position = get_opened_positions(symbol)
            open_sl = position[0]
            quantity = position[1]
            close_position(symbol, open_sl, abs(quantity))



    def telegram_bot_sendtext(bot_message):
        bot_token2 = bot_token
        bot_chatID = chat_id
        send_text = f"https://api.telegram.org/bot{bot_token2}/sendMessage?chat_id={bot_chatID}&parse_mode=Markdown&text={bot_message}"
        return response.json()


    starttime = time.time()
    timeout = time.time() + 60*60*12
    counterr = 1

    while time.time() <= timeout
        try:
            print("passthroug at "+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            gerTPSLfrom_telegram()
            time.sleep(15 - ((time.time() - starttime) % 15.0))
        except KeyboardInterrupt:
            print('\n\nKeyboard exception received. Exiting')
            exit()