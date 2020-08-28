from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import math, datetime
import numpy as np
import pickle
style.use('seaborn-whitegrid')

api_key = process.env.ALPHA_VANTAGE_API

def get_stockdata(symbol, begin='1990-01-01'):
    ts = TimeSeries(key=api_key, output_format='pandas', indexing_type='date')
    df, meta_data = ts.get_daily_adjusted(symbol=symbol, outputsize='full')
    df.index = pd.to_datetime(df.index)
    df = df[['5. adjusted close']]
    df.rename(columns={'5. adjusted close':'%s close'%symbol}, inplace=True)

    return df.truncate(before=begin)

def get_intraday_stockdata(symbol, begin='1990-01-01'):
    ts = TimeSeries(key=api_key, output_format='pandas', indexing_type='date')
    df, meta_data = ts.get_intraday(symbol=symbol, interval='15min', outputsize='full')
    print (df.head())
    df.index = pd.to_datetime(df.index)
    df = df[['4. close']]
    df.rename(columns={'4. close':'%s close' % symbol}, inplace=True)

    print (df.head())
    return df.truncate(before=begin)

def get_mas(df, ticker, short, long, emas=True):
    '''
    df: Pandas DF with closing value of stock
    short: int representing length of short MA
    long: int representing length of long MA
    '''
    # ema_short = df.ewm(span=20, adjust=False).mean()
    # print ('__________________________')
    # print (ema_short)
    # print ('__________________________')
    if emas:
        df['%s shortema' % ticker] = df['%s close' % ticker].ewm(span=short, adjust=False).mean()
        df['%s longema' % ticker] = df['%s close' % ticker].ewm(span=long, adjust=False).mean()
        df['%s Fast MACD Line'%ticker] = df['%s shortema'%ticker]-df['%s longema'%ticker]
        df['%s Signal MACD Line'%ticker] = df['%s Fast MACD Line'%ticker].ewm(span=int(short*.75), adjust=False).mean()
    else:
        df['%s shortsma' % ticker] = df['%s close' % ticker].rolling(short).mean()
        df['%s longsma' % ticker] = df['%s close' % ticker].rolling(long).mean()
    return df

class Error(Exception):
    pass

class doubleorderBuy(Error):
    print ('2 Buys in row')
class doubleorderSell(Error):
    print ('2 Sells in a row')

def validation(df, ticker, type):
    previous = 0
    # print (previous)
    # print (df['%s signal'% ticker])
    for signal in df['{} {} signal'.format(ticker, type)]:
        # print (previous)
        if signal != 0 and signal == previous:
            if signal == 1:
                raise doubleorderBuy
            else: raise doubleorderSell
        elif signal != previous and signal != 0:
            previous = signal

def ema_cross_signals(df, ticker, emas=True):
    type = "EMA Cross"

    if emas:
        df['%s direction' % ticker] = df['%s longema' % ticker]-df['%s longema' % ticker].shift(1) #finds direction of long MA
    else:
        df['%s direction' % ticker] = df['%s longsma' % ticker]-df['%s longsma' % ticker].shift(1) #finds direction of long MA

    df.dropna(inplace=True) #Drop the nans

    # print (df)
    signal = []
    for i in df.index:
        close = df['%s close'%ticker][i]
        dir = df['%s direction'%ticker][i]
        if emas:
            shortema = df['%s shortema'%ticker][i]
            longema = df['%s longema'%ticker][i]
            if shortema >= longema:# and dir > 0:
                signal.append(1)
            elif shortema < longema:
                signal.append(-1)
            else:
                signal.append(0)
        else:
            shortsma = df['%s shortsma'%ticker][i]
            longsma = df['%s longsma'%ticker][i]
            if shortsma >= longsma:# and dir > 0:
                signal.append(1)
            elif shortsma < longsma:
                signal.append(-1)
            else:
                signal.append(0)

    first = signal[0]
    for i in range(1, len(signal)):
        if signal[i] == first:
            signal[i] = 0
        else:
            first = signal[i]


    df['{} {} signal'.format(ticker, type)] = signal
    df = tester(df, ticker, type)
    validation(df, ticker, type)
    return df

def ema_price_cross_signals(df, ticker, emas=True):
    df.dropna(inplace=True) #Drop the nans
    type = "EMA Price Cross"

    # print (df)
    signal = []
    for i in df.index:
        close = df['%s close'%ticker][i]
        # dir = df['%s direction'%ticker][i]
        if emas:
            longema = df['%s longema'%ticker][i]
            if longema >= close:# and dir > 0:
                signal.append(-1)
            elif longema < close:
                signal.append(1)
            else:
                signal.append(0)
        else:
            longsma = df['%s longsma'%ticker][i]
            if longsma >= close:# and dir > 0:
                signal.append(1)
            elif longsma < close:
                signal.append(-1)
            else:
                signal.append(0)

    first = signal[0]
    for i in range(1, len(signal)):
        if signal[i] == first:
            signal[i] = 0
        else:
            first = signal[i]


    df['{} {} signal'.format(ticker, type)] = signal
    df = tester(df, ticker, type)
    validation(df, ticker, type)
    return df

def MACD_signals(df, ticker):
    type = "MACD Cross"
    df.dropna(inplace=True) #Drop the nans

    signal = []
    for i in df.index:
        close = df['%s close'%ticker][i]
        # dir = df['%s direction'%ticker][i]
        fastMACD = df['%s Fast MACD Line'%ticker][i]
        signalMACD = df['%s Signal MACD Line'%ticker][i]
        if fastMACD >= signalMACD:# and dir > 0:
            signal.append(1)
        elif fastMACD < signalMACD:
            signal.append(-1)
        else:
            signal.append(0)


    first = signal[0]
    for i in range(1, len(signal)):
        if signal[i] == first:
            signal[i] = 0
        else:
            first = signal[i]


    df['{} {} signal'.format(ticker, type)] = signal
    df = tester(df, ticker, type)
    validation(df, ticker, type)
    return df

def tester(df, ticker, type, principal=10**5):
    principal = principal # $100,000 start
    numshares = []
    capital = []
    value = [] #Holds value at each time step
    # print (df.head())
    shares = 0
    for i in df.index:
        if df['{} {} signal'.format(ticker,type)][i] == 1: #Buy Signal
            tobuy = int(principal/df['%s close' % ticker][i]) #Divide principal by closing price
            cost = tobuy * df['%s close' % ticker][i] #Find cost of shares
            principal -= cost
            shares += tobuy
            value.append(principal + df['%s close' % ticker][i]*shares)
            numshares.append(shares)
            capital.append(principal)
        elif df['{} {} signal'.format(ticker,type)][i] == -1:
            tosell = shares
            cost = tosell * df['%s close' % ticker][i]
            principal += cost
            shares -= tosell
            value.append(principal + df['%s close' % ticker][i]*shares)
            numshares.append(shares)
            capital.append(principal)
        else:
            value.append(principal + df['%s close' % ticker][i]*shares)
            numshares.append(shares)
            capital.append(principal)
            continue

    df['{} {} value'.format(ticker, type)] = value
    # df['%s numshares' % ticker] = numshares
    # df['%s capital' % ticker] = capital

    return df

def profit_MAs(df, ticker, min=1, max=20):

    profit = []
    for short in range(min, max+1, 5):
        for long in range(short+1, max+1, 5):
            print (short, long)

            ndf = get_smas(df, ticker, short, long)
            ndf = ndf.truncate(before='2015-01-02', after='2018-03-01')
            ndf = buy_sell_signals(ndf, ticker)
            ndf = tester(ndf, ticker)
            value = ndf['%s value' % ticker][-1]

            profit.append((value, short, long))

    return profit

def best_MAs(profitMAs, topN = 3):
    order = sorted(profitMAs, reverse=True)
    return order[:topN]


if __name__ == '__main__':

    ticker = 'AMZN'
    df = get_stockdata(ticker)
    # df.to_pickle('%s.pickle'%ticker)

    # df = pd.read_pickle('%s.pickle'%ticker)
    df = pd.read_csv('stock_dfs/%s.csv'%ticker)
    df.set_index('date', inplace=True)
    df.rename(columns = {'close': '%s close'% ticker}, inplace=True)
    df.drop(['volume'], 1, inplace=True)

    # print (df)
    shortsma = 181
    longsma = 182

    # profit = profit_MAs(df, ticker, min=1, max =200)
    # with open('profitMA.pickle', 'wb') as f:
    #     pickle.dump(profit, f)
    #
    # with open('profitMA.pickle', 'rb') as f:
    #     profit = pickle.load(f)
    # print (best)
    # print (best_MAs(profit))

    # print (df.head())
    df = get_smas(df, ticker, shortsma, longsma)

    df = df.truncate(before='2015-01-02', after='2018-03-01')
    df = buy_sell_signals(df, ticker)

    # print (df.head())

    df = tester(df, ticker)

    # print (df)

    # df['value'] = profit
    # df['shares'] = shares
    # df['capital'] = money


    print (df['%s value' % ticker][-1]) #Overall value

    fig, ax1 = plt.subplots()

    # plt.plot(profit)
    df['%s close' % ticker].plot(ax=ax1)
    df['%s shortsma' % ticker].plot(ax=ax1, label='%s day sma' % (str(shortsma), ))
    df['%s longsma' % ticker].plot(ax=ax1, label='%s day sma' % (str(longsma), ))
    plt.legend()
    ax2 = ax1.twinx()
    df['%s value' % ticker].plot(ax=ax2, color='k')

    for date in df.index:
        element = df['%s signal' % ticker][date]

        # print (date)
        if element == 1:
            plt.axvline(date, color='g')
        elif element == -1:
            plt.axvline(date, color='r')
        else:
            pass


    plt.legend()

    print (df.head())
    print (df.tail())
    # print (df)
    fig.tight_layout()
    plt.show()
