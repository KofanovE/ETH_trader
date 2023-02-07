import copy
import time
import random
import logging
import numpy as np
import pandas as pd
import statsmodels.api as sm
import requests

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from futures_sign import send_signed_request, send_public_request
from binance_functions import *
from Indicators import *
from telegram_bot import *

global client, symbol, maxposition

# Logging setup
logger = logging.getLogger("_Main")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("main_log.log")
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.debug(f"\n\n\n")
logger.warning(f"Start program: {time.strftime('%d.%m.%Y  %H:%M:%S', time.localtime(time.time()))}")

# Setup of trading parameters
symbol = 'ETHUSDT'
maxposition = 0.1
stop_percent = 0.01                                                                             # 0.01 = 1%
eth_proffit_array = [[11, 1], [22, 1], [32, 2], [43, 2], [54, 2], [80, 1], [106, 1], [106, 0]]  #take profit steps in percents for 1600 usdt/eth
proffit_array = copy.copy(eth_proffit_array)

pointer = str(random.randint(1000, 9999))                                                       # id of new trading bot


def main(step):
    """
    Main function for processing signals from input functions and control of output functions.

    :param step: digit of cycle for sending information to telegram_bot
    :type step: int
    """
    global proffit_array

    try:
        # Getting initialization information
        position = get_opened_positions(symbol)                             # getting correct information from binance
        open_sl = position[0]                                               # correct signal
        logger.debug(f"Current position: {open_sl}")

        # Getting command from telegram_bot
        msg = getTPSLfrom_telegram()
        if msg == 'quit':
            quit()
        elif msg == 'exit':
            exit()
        elif msg == 'hello':
            telegram_bot_sendtext('Hello, how are you?')
        elif msg == 'open_short':
            telegram_bot_sendtext('Ok, open short.')
            open_position(symbol, 'short', maxposition)
        elif msg == 'open_long':
            telegram_bot_sendtext('Ok, open long.')
            open_position(symbol, 'long', maxposition)
        elif msg == 'close_pos':
            telegram_bot_sendtext('Ok, close position.')
            position = get_opened_positions(symbol)
            open_sl = position[0]
            quantity = position[1]
            close_position(symbol, open_sl, abs(quantity))

        # No current deal subcycle
        if open_sl == "":
            if step == 5:
                prt(f'No open position.')

            check_and_close_orders(symbol)                                  # close all opened positions to binance
            signal = check_if_signal(symbol)                                # check Long or Short signal
            proffit_array = copy.copy(eth_proffit_array)                    # getting new array of take profit steps

            logger.debug(f"No open position: {symbol} Signal : {signal}")

            # If there ia a signal - open position
            if signal == "long":
                open_position(symbol, 'long', maxposition)
            elif signal == 'short':
                open_position(symbol, 'short', maxposition)

        # Subcycle of the presence of the current deal
        else:
            entry_price = position[5]                                       # check enter price
            current_price = get_symbol_price(symbol)                        # check current price
            quantity = position[1]                                          # get information about current number of opened positions

            logger.info(f"Founded open position: {symbol} : {quantity}({open_sl})")


            # Subcycle: If current deal is Long
            if open_sl == "long":
                # The mechanism of trailing stop
                if len(proffit_array) < 8:
                    trailing_price = entry_price + eth_proffit_array[-(len(proffit_array) + 1)][0]
                else:
                    trailing_price = entry_price

                stop_price = trailing_price * (1 - stop_percent)            # getting current stop_price
                # Subcycle: Stop Loss for Long deal
                if current_price < stop_price:
                    logger.info(f"Long -> Stop Loss: {current_price} < {stop_price}")
                    close_position(symbol, 'long', abs(quantity))           # closing current position
                    proffit_array = copy.copy(eth_proffit_array)            # getting new profit array
                # Subcycle: not Stop Loss for Long deal
                else:
                    temp_arr = copy.copy(proffit_array)                     # getting current profit array from new
                    tp_current = entry_price + temp_arr[0][0]
                    # Getting of max step profit array
                    for j in range(0, len(temp_arr) - 1):
                        delta = temp_arr[j][0]
                        contracts = temp_arr[j][1]
                        # Subcycle: Take Profit for Long deal
                        if current_price > entry_price + delta:
                            logger.info(f"Long -> Take Profit ({abs(round(maxposition * (contracts / 10), 3))}): {current_price} > {entry_price + delta}")
                            close_position(symbol, 'long', abs(round(maxposition * (contracts / 10), 3)))   # closing one current profit postition
                            del proffit_array[0]                                                            # deleting closed profit position from profit array

            # Subcycle: If current deal is Short
            if open_sl == "short":
                # The mechanism of trailing stop
                if len(proffit_array) < 8:
                    trailing_price = entry_price - eth_proffit_array[-(len(proffit_array) + 1)][0]
                else:
                    trailing_price = entry_price

                stop_price = trailing_price * (1 + stop_percent)            # getting current stop_price
                # Subcycle: Stop Loss for Short deal
                if current_price > stop_price:
                    logger.info(f"Short -> Stop Loss: {current_price} > {stop_price}")
                    close_position(symbol, 'short', abs(quantity))          # closing current position
                    proffit_array = copy.copy(eth_proffit_array)            # getting new profit array
                # Subcycle: not Stop Loss for Short deal
                else:
                    temp_arr = copy.copy(proffit_array)                     # getting current profit array from new
                    tp_current = entry_price - temp_arr[0][0]
                    # Getting of max step profit array
                    for j in range(0, len(temp_arr) - 1):
                        delta = temp_arr[j][0]
                        contracts = temp_arr[j][1]
                        # Subcycle: Take Profit for Short deal
                        if current_price < entry_price - delta:
                            logger.info(f"Short -> Take Profit ({abs(round(maxposition * (contracts / 10), 3))}): {current_price} > {entry_price - delta}")
                            close_position(symbol, 'short', abs(round(maxposition * (contracts / 10), 3)))  # closing one current profit postition
                            del proffit_array[0]                                                            # deleting closed profit position from profit array

            if step == 5:
                prt(f'Founded: {open_sl}, Quantity: {quantity}' )
                prt(f'Cur: {current_price}, TP: {round(tp_current, 2)}, SL: {round(stop_price, 2)}, Ent: {round(entry_price, 2)}')
    except:
        logger.error("Information about error: ", exc_info=True)
        prt('\n\nSomething went wrong. Continuig...')



def prt(message):
    """
    Function for sending information to telegram_bot

    :param message: sending message
    :type message: str
    """
    telegram_bot_sendtext(pointer+': '+message)
    print(pointer + ':   ' + message)





"""
Body of program
"""
starttime = time.time()                                     # getting start time
timeout = time.time() + 60 * 60 * 24 * 7                    # time working boot = 24 hours
counterr = 1                                                # initialization counter of sending current information

while time.time() <= timeout:
    try:
        logger.info(f"______________________________________________________________________________________________________________")
        logger.info(f"Script continue running at {time.strftime('%d.%m.%Y  %H:%M:%S', time.localtime(time.time()))}")

        if counterr == 5:
            prt("5th script continue running at "+time.strftime('%Y - %m - %d %H:%M:%S', time.localtime(time.time())))

        # Start main function
        main(counterr)

        counterr += 1
        if counterr > 5:
            counterr = 1
        time.sleep(5 - ((time.time() - starttime) % 5.0))   # 1 minute interval between each new execution

    except KeyboardInterrupt:
        logger.warning(f"KeyboardInterrupt. Stopping: {time.strftime('%d.%m.%Y  %H:%M:%S', time.localtime(time.time()))}")
        print('\n\KeyboardInterrupt. Stopping.')
        exit()
