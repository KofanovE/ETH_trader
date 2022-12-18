import copy

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl
from futures_sign import send_signed_request, send_public_request
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from cred import KEY, SECRET
import requests


from Indicators import *


"""
В PrepareDF функції планується добавити стовпці мін та макс каналу з середніх значеннь з історії, 
позиція в каналі та кут нахилу тренду
"""

def main():


    global client

    symbol = 'ETHUSDT'

    client = Client(KEY, SECRET)

    # open_position(symbol, 'short', 0.006)

    # close_position(symbol, 'short', 0.006)

    # print(get_futures_klines(symbol))

    print(get_opened_positions(symbol))

def get_futures_klines(symbol, limit=500):   #example symple request to binance and get last price
    x = requests.get(f'https://binance.com/fapi/v1/klines?symbol={symbol}&limit={str(limit)}&interval=5m')
    df = pd.DataFrame(x.json())
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'd1', 'd2', 'd3', 'd4', 'd5']
    df = df.drop(['d1', 'd2', 'd3', 'd4', 'd5'], axis=1)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

def open_position(symbol, s_l, quantity_l): #fincion opening position
    sprice = get_symbol_price(symbol)

    if s_l == 'long':
        close_price = str(round(sprice * (1 + 0.01), 2))
        params = {
            'batchOrders': [
                {
                    'symbol': symbol,
                    'side': 'BUY',
                    'type': 'LIMIT',
                    'quantity': str(quantity_l),
                    'timeInForce': 'GTC',
                    'price' : close_price
                }
            ]

        }
        responce = send_signed_request('POST', '/fapi/v1/batchOrders', params)
    if s_l == 'short':
        close_price = str(round(sprice * (1 - 0.01), 2))
        params = {
            'batchOrders': [
                {
                    'symbol': symbol,
                    'side': 'SELL',
                    'type': 'LIMIT',
                    'quantity': str(quantity_l),
                    'timeInForce': 'GTC',
                    'price' : close_price
                }
            ]

        }
        responce = send_signed_request('POST', '/fapi/v1/batchOrders', params)


def close_position(symbol, s_l, quantity_l): #function closing position
    sprice = get_symbol_price(symbol)

    if s_l == 'long':
        close_price = str(round(sprice * (1 - 0.01), 2))
        params = {
            'batchOrders': [
                 {
                    'symbol': symbol,
                    'side': 'SELL',
                    'type': 'LIMIT',
                    'quantity': str(quantity_l),
                    'timeInForce': 'GTC',
                    'price': close_price
                }
                            ]
                }
        responce = send_signed_request('POST', '/fapi/v1/batchOrders', params)

    if s_l == 'short':
        close_price = str(round(sprice * (1 + 0.01), 2))
        params = {
            'batchOrders': [
                 {
                    'symbol': symbol,
                    'side': 'BUY',
                    'type': 'LIMIT',
                    'quantity': str(quantity_l),
                    'timeInForce': 'GTC',
                    'price': close_price
                }
                            ]
                }
        responce = send_signed_request('POST', '/fapi/v1/batchOrders', params)


def get_opened_positions(symbol): # function gettion information about opened prices
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    a = positions[positions['symbol'] == symbol]['positionAmt'].astype(float).tolist()[0]
    leverage = int(positions[positions['symbol'] == symbol]['leverage'])
    entryprice = positions[positions['symbol'] == symbol]['entryPrice']
    profit = float(status['totalUnrealizedProfit'])
    balance = round(float(status['totalWalletBalance']), 2)
    if a > 0:
        pos = 'long'
    elif a < 0:
        pos = 'short'
    else:
        pos = ""
    return [pos, a, profit, leverage, balance, round(float(entryprice), 3), 0]

def check_and_close_orders(symbol):
    global isStop
    a = client.futures_get_open_orders(symbol=symbol)
    if len(a) > 0:
        isStop = False
        client.futures_cancel_all_open_orders(symbol=symbol)


def get_symbol_price(symbol):
    prices = client.get_all_tickers()
    df = pd.DataFrame(prices)
    return float(df[df['symbol'] == symbol]['price'])







"""

    pd.set_option('display.max_columns', None)  #форматування відображення DataFrame
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    lend = len(prepared_df)
    prepared_df['hcc'] = [None] * lend
    prepared_df['lcc'] = [None] * lend
    for i in range(4, lend-1):
        if isHCC(prepared_df, i) > 0:
            prepared_df.at[i, 'hcc'] = prepared_df['close'][i]
        if isLCC(prepared_df, i) > 0:
            prepared_df.at[i, 'lcc'] = prepared_df['close'][i]






    # Тестова стратегія
    #________________________________________________________________________________________________
    deal = 0
    position = 0
    eth_proffit_array = [[20, 1], [40, 1], [60, 2], [80, 2], [100, 2], [150, 1], [200, 1], [200, 0]]

    prepared_df['deal_o'] = [None] * lend  #open
    prepared_df['deal_c'] = [None] * lend  #close
    prepared_df['earn'] = [None] * lend    #earn


    for i in range(4, lend-1):
        prepared_df.at[i, 'earn'] = deal
        if position > 0:                               #if open position which contract > 0 = Long
            #long
            if prepared_df['close'][i] < stop_prise:   # if actual price < stop price
                #stop_loss
                deal = deal - (open_price-prepared_df['close'][i]) # added loss to deal
                position = 0                                       # clossed position
                prepared_df.at[i, 'deal_c'] = prepared_df['close'][i] # write in deal_close actual price
            else:
                temp_arr = copy.copy(proffit_array)
                for j in range(0, len(temp_arr) - 1):
                    delta = temp_arr[j][0]
                    contracts = temp_arr[j][1]
                    if prepared_df['close'][i] > open_price + delta:
                        prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
                        position = position - contracts
                        deal = deal + (prepared_df['close'][i] - open_price)*contracts
                        del proffit_array[0]

        elif position < 0:
            #short
            if prepared_df['close'][i] > stop_prise:
                #stop loss
                deal = deal - prepared_df['close'][i] - open_price
                position = 0
                prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
            else:
                temp_arr = copy.copy(proffit_array)
                for j in range(0, len(temp_arr)-1):
                    delta = temp_arr[j][0]
                    contracts = temp_arr[j][1]
                    if prepared_df['close'][i] < open_price - delta:
                        prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
                        position = position + contracts
                        deal = deal + (open_price - prepared_df['close'][i]) * contracts
                        del proffit_array[0]
        else:
            if prepared_df['lcc'][i-1] != None:
                #Long
                if prepared_df['position_in_channel'][i-1] < 0.5:
                    if prepared_df['slope'][i-1] < -20:
                        prepared_df.at[i, 'deal_o'] = prepared_df['close'][i]
                        proffit_array = copy.copy(eth_proffit_array)
                        position = 10
                        open_price = prepared_df['close'][i]
                        stop_prise = prepared_df['close'][i]*0.99
            if prepared_df['hcc'][i - 1] != None:
                # Short
                if prepared_df['position_in_channel'][i-1] > 0.5:
                    if prepared_df['slope'][i - 1] > -20:
                        prepared_df.at[i, 'deal_o'] = prepared_df['close'][i]
                        proffit_array = copy.copy(eth_proffit_array)
                        position = -10
                        open_price = prepared_df['close'][i]
                        stop_prise = prepared_df['close'][i] * 1.01

    print(prepared_df)

    # Visualization
    aa = prepared_df[0:1000]
    aa = aa.reset_index()

    labels = ['close', 'deal_o', 'deal_c'] #, 'channel_max', 'channel_min'
    labels_line = ['--', '*-', '*-', 'g-', 'r-']

    j = 0
    x = pd.DataFrame()
    y = pd.DataFrame()
    for i in labels:
        x[j] = aa['index']
        y[j] = aa[i]
        j += 1

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

    fig.suptitle("Deals")
    fig.set_size_inches(20, 10)

    for j in range(0, len(labels)):
        ax1.plot(x[j], y[j], labels_line[j])

    ax1.set_ylabel("Price")
    ax1.grid(True)

    ax2.plot(x[0], aa['earn'], 'g-') #EMA
    ax3.plot(x[0], aa['position_in_channel'], '.-')

    ax2.grid(True)
    ax3.grid(True)
    plt.show()

"""

if __name__ == "__main__":
    main()