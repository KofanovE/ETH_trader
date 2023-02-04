import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl
import copy
from sklearn.linear_model import LinearRegression

import binance_functions as bf


def PrepareDF(DF):
    """
    Function formats data frame and adds columns with current slopes and positions in channel

    :param DF: data frame with trading candles of current coin
    :type DF: data frame (pandas)
    :return: data frame with added columns of slope and points of positions in channel
    :type return: data frame (pandas)
    """
    ohlc = DF
    ohlc.columns = ["date", "open", "high", "low", "close", "volume", "date_2"]
    ohlc = ohlc.set_index('date')
    df = ohlc.reset_index()
    df['slope'] = indSlope(df['close'], 5)
    df['chanel_max'] = df['high'].rolling(10).max()
    df['chanel_min'] = df['low'].rolling(10).min()
    df['position_in_channel'] = (df['close'] - df['chanel_min']) / (df['chanel_max'] - df['chanel_min'])
    df = df.set_index('date')
    df = df.reset_index()
    return df


def indSlope(series, n):
    """
    Function calculates the slope of the trend

    :param series: array with data of close positions of trading candles
    :type series: list
    :param n: number of previous candles to calculate the slope
    :type n: int
    :return: array (numpy) of data with slopes of trend
    """
    array_sl = [j * 0 for j in range(n-1)]
    for j in range(n, len(series)+1):
        y = series[j-n:j]
        x = np.array(range(n))
        x_sc = (x - x.min()) / (x.max() - x.min())
        y_sc = (y - y.min()) / (y.max() - y.min())
        x_sc = sm.add_constant(x_sc)
        model = sm.OLS(y_sc, x_sc)
        results = model.fit()
        array_sl.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(array_sl))))
    return np.array(slope_angle)


def isLCC(DF, i):
    """
    The function of determining the local minimum of the trend

    :param DF: data frame (pandas) with trading candles of current coin
    :param i: number (int) of current candle for determining the local minimum
    :return: numer (int) of current candle if there is a signal of the local minimum
    """
    df = DF.copy()
    LCC = 0
    if df['close'][i] <= df['close'][i+1] and df['close'][i] <= df['close'][i-1] and df['close'][i+1] > df['close'][i-1]:
        LCC = i - 1
    return LCC


def isHCC(DF, i):
    """
    The function of determining the local maximum of the trend

    :param DF: data frame (pandas) with trading candles of current coin
    :param i: number (int) of current candle for determining the local maximum
    :return: numer (int) of current candle if there is a signal of the local maximum
    """
    df = DF.copy()
    HCC = 0
    if df['close'][i] >= df['close'][i + 1] and df['close'][i] >= df['close'][i - 1] and df['close'][i + 1] < df['close'][i - 1]:
        HCC = i
    return HCC


def check_if_signal(symbol):
    """
    The function analyzes data from auxiliary indicators and gives a signal to open a position

    :param symbol: name of coin (str)
    :return: signal of open position (str)
    """
    ohlc = bf.get_futures_klines(symbol, 100)       # get last 100 candles
    prepared_df = PrepareDF(ohlc)
    signal = ""                                     #return value
    i = 98                                          # 99 is current kandel which is not clossed, 98 is last closed candel, we need 97 to check it is bottom or top

    if isLCC(prepared_df, i - 1) > 0:
        # found bottom -  OPEN LONG
        if prepared_df['position_in_channel'][i-1] < 0.1:
            #close to top of channel
            # if prepared_df['slope'][i-1] > 20:
            #found a good enter point for Long
            signal = 'long'
    if isHCC(prepared_df, i - 1) > 0:
        #found top - OPEN SHORT
        if prepared_df['position_in_channel'][i-1] > 0.9:
            #close to top of channel
            # if prepared_df['slope'][i-1] > 20:
            # found a good enter point for Short
            signal = 'short'
    return signal


