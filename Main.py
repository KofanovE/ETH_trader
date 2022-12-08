import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl


from Indicators import PrepareDF


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
    prepared_df[0:100]['close'].plot()
    plt.show()





if __name__ == "__main__":
    main()