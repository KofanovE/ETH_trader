import copy

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl


from Indicators import *


"""
В PrepareDF функції планується добавити стовпці мін та макс каналу з середніх значеннь з історії, 
позиція в каналі та кут нахилу тренду
"""

def main():

    pd.set_option('display.max_columns', None)  #форматування відображення DataFrame
    # pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    # api_key = "8T4KQAIG4PFXRYSG"
    # api_key = 'LSZH501HZPZVU1GA'
    # interval_var = '15min'
    # symbol = 'BTC'

    # url = f'https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol={symbol}&market=USD&interval={interval_var}&apikey={api_key}&datatype=csv&outputsize=full'
    url = f'https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=ETH&market=USD&interval=5min&apikey=demo&datatype=csv'
    df = pd.read_csv(url)
    df = df[::-1]                                       # [timestamp, open, high, low, close, volume]
    prepared_df = PrepareDF(df)

    # prepared_df[0:100][['slope']].plot()
    # prepared_df[0:100][['close']].plot()
    # prepared_df[0:100][['close', 'chanel_max', 'chanel_min']].plot()
    # plt.show()

    lend = len(prepared_df)
    prepared_df['hcc'] = [None] * lend
    prepared_df['lcc'] = [None] * lend
    for i in range(4, lend-1):
        if isHCC(prepared_df, i) > 0:
            prepared_df.at[i, 'hcc'] = prepared_df['close'][i]
        if isLCC(prepared_df, i) > 0:
            prepared_df.at[i, 'lcc'] = prepared_df['close'][i]


    aa = prepared_df[0:200]
    aa = aa.reset_index()

    labels = ['close', 'hcc', 'lcc', 'chanel_max', 'chanel_min']
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

    ax2.plot(x[0], aa['slope'], '.-') #EMA
    ax3.plot(x[0], aa['position_in_channel'], '.-')

    ax2.grid(True)
    ax3.grid(True)

    plt.show()

    # Тестова стратегія
    #________________________________________________________________________________________________
    deal = 0
    position = 0
    eth_proffit_array = [[20, 1], [40, 1], [60, 2], [80, 2], [100, 2], [150, 1], [200, 1], [200, 0]]

    for i in range(4, lend-1):
        if position > 0:
            #long
            if prepared_df['close'][i] < stop_prise:
                #stop_loss
                deal = deal - (open_price-prepared_df['close'][i])
                position = 0
                print('stop loss')
            else:
                print(i, position, proffit_array)
                temp_arr = copy.copy(proffit_array)
                for j in range(0, len(temp_arr) - 1):
                    delta = temp_arr[j][0]
                    contracts = temp_arr[j][1]
                    if prepared_df['close'][i] > open_price + delta:
                        position = position - contracts
                        deal = deal + (prepared_df['close'][i] - open_price)*contracts
                        del proffit_array[0]

        elif position < 0:
            #short
            pass
        else:
            if prepared_df['lcc'][i-1] != None:
                #Long
                if prepared_df['position_in_channel'][i-1] < 0.5:
                    if prepared_df['slope'][i-1] < -20:
                        print(i, 'open long position')
                        proffit_array = copy.copy(eth_proffit_array)
                        position = 10
                        open_price = prepared_df['close'][i]
                        stop_prise = prepared_df['close'][i]*0.99
            if prepared_df['hcc'][i - 1] != None:
                # Short
                if prepared_df['position_in_channel'][i-1] > 0.5:
                    if prepared_df['slope'][i - 1] > -20:
                        print(i, 'open short position')
                        proffit_array = copy.copy(eth_proffit_array)
                        position = -10
                        open_price = prepared_df['close'][i]
                        stop_prise = prepared_df['close'][i] * 1.01


if __name__ == "__main__":
    main()