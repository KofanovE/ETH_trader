import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl
"""
В результаті отримано тестовий датафрейм з цінами барів та графік мін, макс та закриття барів
"""
def main():
    api_key = 'LSZH501HZPZVU1GA'
    interval_var = '15min'
    symbol = 'BTC'

    url = f'https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol={symbol}&market=USD&interval={interval_var}&apikey={api_key}&datatype=csv&outputsize=full'
    df = pd.read_csv(url)
    df = df[::-1]
    frame = pd.DataFrame(df[['high', 'low', 'close']])  # Тестовий датафрейм
    print(frame)
    frame[['high', 'low']].plot()
    plt.show()



if __name__ == "__main__":
    main()