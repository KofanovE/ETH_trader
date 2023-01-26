import requests
import time
from cred import bot_token, chat_id
from binance_functions import get_opened_positions, open_position, close_position
global symbol, maxposition


telegram_delay = 13

def getTPSLfrom_telegram(symbol, maxposition, start_prog_time ):
    global old_datet, flag_new_message, old_open_sl, old_quantity

    strr = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(strr)
    rs = response.json()
    rs2 = rs['result'][-1]
    rs3 = rs2['message']
    textt = rs3['text']
    datet = rs3['date']

    position = get_opened_positions(symbol)
    open_sl = position[0]
    quantity = position[1]

    # print(textt, "\n")
    # print(time.time(), datet, time.time()-datet, telegram_delay)
    if start_prog_time > datet:
        old_datet = start_prog_time
        flag_new_message = False # start_program
        old_open_sl = 0
        old_quantity = 0
    elif datet > old_datet and textt in ("open_short", "open_long", "close_pos"):
        old_datet = datet
        flag_new_message = True
        old_open_sl = open_sl
        old_quantity = quantity

    print(f"flag_new_message = {flag_new_message}")
    print(f"old_datet = {old_datet}")
    print(f"old_open_sl = {old_open_sl}, old_quantity = {old_quantity}")
    print(f"open_sl = {open_sl}, quantity = {quantity}")
    if (time.time() - datet) < telegram_delay:
        print("pic")
        if 'quit' in textt:
            quit()
        if 'exit' in textt:
            exit()
        if 'hello' in textt:
            telegram_bot_sendtext('Hello, how are you?', symbol, maxposition, start_prog_time)

    if flag_new_message:
        print(f"New message: {textt}")
        telegram_bot_sendtext(f"New message: {textt}", symbol, maxposition, start_prog_time)
        if 'open_short' in textt:
            if quantity > old_quantity - maxposition:
                open_position(symbol, 'short', maxposition)
            else:
                flag_new_message = False
        if 'open_long' in textt:
            if quantity < old_quantity + maxposition:
                open_position(symbol, 'long', maxposition)
            else:
                flag_new_message = False
        if 'close_pos' in textt:
            if quantity != 0:
                close_position(symbol, open_sl, abs(quantity))
            else:
                flag_new_message = False
                old_open_sl = open_sl
                old_quantity = quantity


def telegram_bot_sendtext(bot_message, symbol, maxposition, start_prog_time):
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
            getTPSLfrom_telegram(symbol, maxposition, strat_prog_time)
            time.sleep(15 - ((time.time() - starttime) % 15.0))
        except KeyboardInterrupt:
            print('\n\nKeyboard exception received. Exiting')
            exit()