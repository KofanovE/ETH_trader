"""
В PrepareDF функції планується добавити стовпці мін та макс каналу з середніх значеннь з історії,
позиція в каналі та кут нахилу тренду
"""


def PrepareDF(DF):                                                     # Функція формування повного датафрейму
    ohlc = DF
    ohlc.columns = ["date", "open", "high", "low", "close", "volume"]  # Зміна назв колонок датафрейму
    ohlc = ohlc.set_index('date')
    #print(ohlc)




"""
TR = max[(H-L), |H-Cp|, |L-Cp|]
ATR = 1/n * sum(TR)
TR: a particular True Range
n: the time period employed
H: current High
L: current Low
Cp: previous close
"""
def indATR(source_DF, n):
    df = source_DF.copy()
    df['H-L']=abs(df['high']-df['low'])                          # H - L
    df['H-PC']=abs(df['high']-df['close'].shift(1))
    df['L-PC']=abs(df['low']-df['close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False) # TR
    df['ATR'] = df['TR'].rolling(n).mean()                      # ATR = Середня в роллінгі TR за 14 рядків
    df_temp = df.drop(['H-L','H-PC','L-PC'],axis=1)            # Видалення технічних колонок
    #return df_temp
    print(df[['high', 'low', 'close', 'H-PC']])