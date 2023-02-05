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

global client
client = Client(KEY, SECRET, testnet=True)



def get_futures_klines(symbol, limit=500):
    """
    The functon sends equest to binance and get last price

    :param symbol: name of coin (str)
    :param limit: limit of time to get response (int)
    :return: data frame (pandas)
    """
    # x = requests.get(f'https://binance.com/fapi/v1/klines?symbol={symbol}&limit={str(limit)}&interval=5m')
    x = requests.get(f'https://testnet.binancefuture.com/fapi/v1/klines?symbol={symbol}&limit={str(limit)}&interval=5m')

    df = pd.DataFrame(x.json())
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'd1', 'd2', 'd3', 'd4', 'd5']
    df = df.drop(['d1', 'd2', 'd3', 'd4', 'd5'], axis=1)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df



def open_position(symbol, s_l, quantity_l):
    """
    The function sends a request to binance for opening position

    :param symbol: name of coin (str)
    :param s_l: type of opening position - long/short (str)
    :param quantity_l: quantity opening position (float)
    :return: None
    """
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
        send_signed_request('POST', '/fapi/v1/batchOrders', params)
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
        send_signed_request('POST', '/fapi/v1/batchOrders', params)



def close_position(symbol, s_l, quantity_l):
    """
    The function sends a request to binance for closing position

    :param symbol: name of coin (str)
    :param s_l: type of closing position - long/short (str)
    :param quantity_l: quantity closing position (float)
    :return: None
    """
    sprice = get_symbol_price(symbol)

    print("stop loss1:", symbol, s_l, quantity_l)
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
        send_signed_request('POST', '/fapi/v1/batchOrders', params)

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
        send_signed_request('POST', '/fapi/v1/batchOrders', params)



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
