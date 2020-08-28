import trend
import datagrabber
import portfolio

import pandas_datareader as web
import datetime as dt
import os
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib import style
style.use('seaborn-whitegrid')


def compile_data(tickers, short, long, start_date='1960-01-01'):

    all_df = pd.DataFrame()
    numstocks = len(tickers)

    for ticker, count in enumerate(tickers):
        print (ticker, )
        try:
            df = pd.read_pickle('stock_dfs/%s.pickle' % ticker)
            df = df[['close']]
            df.rename(columns={'close':'%s close'%ticker}, inplace=True)
            # df.index = pd.to_datetime(df.index)
        except:
            continue

        df = trend.get_mas(df, ticker, short, long)
        df = df.truncate(before=start_date)
        df = trend.ema_cross_signals(df, ticker)
        df = trend.ema_price_cross_signals(df, ticker)
        df = trend.MACD_signals(df, ticker)
        eachstockprinc = 10**5/numstocks
        # df = trend.tester(df, ticker, principal=eachstockprinc)

        if all_df.empty:
            all_df = df
        else:
            all_df = all_df.join(df, how='outer')

    return all_df

def profit_compare(tickers, df, plot=False):
    holdlist = []
    # df = pd.DataFrame()
    types = ['EMA Cross', "EMA Price Cross", 'MACD Cross']
    for ticker in tickers:

        ticklist = [ticker]
        try:
            for type in types:
                    stratvalue = df['{} {} value'.format(ticker,type)][-1]
                    ticklist.append(stratvalue)

            initialshares = int(df['{} {} value'.format(ticker,type)][0]/df['%s close'%ticker][0])
            finalholdvalue = initialshares * df['%s close'%ticker][-1]
            ticklist.append(finalholdvalue)
            holdlist.append(ticklist)
        except:
            continue

    # print (holdlist)

    columns = ['EMA Cross Value', 'EMA Price Cross Value',
                "MACD Cross Value", 'Buy and Hold Value']

    # print (df.head())
    # print (holdlist)
    profit = pd.DataFrame(holdlist)
    # print (profit.head())
    profit.set_index(0, inplace=True)
    profit.columns = columns
    # print (df)
    # df.rename(columns={0:'Ticker',1:'Strategy Value', 2:'Buy and Hold Val'}, inplace=True)
    # df.set_index('Ticker', inplace=True)

    # if plot:
    #     df.plot.bar()
    #     plt.show()

    return profit

def plotter(ticker, type):
    fig = plt.figure()

    ax1 = plt.subplot2grid((2,1),(0,0))
    ax2 = plt.subplot2grid((2,1),(1,0), sharex=ax1)

    # ax1 = axes[0]
    # ax2 = axes[1]
    # axes[0].plot(profit)
    main_df['%s close' % ticker].plot(ax=ax1)
    # print (type(main_df.index[0]))

    for date in main_df.index:
        element = main_df['{} {} signal'.format(ticker, type)][date]

        if element == 1:
            ax1.axvline(date, color='g')
        elif element == -1:
            ax1.axvline(date, color='r')
        else:
            pass
    main_df['%s shortema' % ticker].plot(ax=ax1, label='%s day ema' % (str(short), ))
    main_df['%s longema' % ticker].plot(ax=ax1, label='%s day ema' % (str(long), ))
    ax1.legend()

    # main_df['%s value' % ticker].plot(ax=ax2, color='k')
    fastMACD = main_df['%s Fast MACD Line'%ticker]
    signalMACD = main_df['%s Signal MACD Line'%ticker]

    # ax2 = ax1.twinx()
    fastMACD.plot(ax=ax2)
    signalMACD.plot(ax=ax2)


    ax2.legend()

    plt.show()

short = 13
long = 26

with open('sp500tickers.pickle', 'rb') as f:
    alltickers = pickle.load(f)
tickers = alltickers[:]

main_df = compile_data(tickers, short, long)
with open('maindf.pickle', 'wb') as f:
    pickle.dump(main_df, f)
#
# with open('maindf.pickle', 'rb') as f:
#     main_df = pickle.load(f)

# df = pd.DataFrame()
df = pd.read_pickle('stock_dfs/AAPL.pickle')
# df = trend.get_mas(df, ticker, short, long)
# df = df.truncate(before=start_date)
# df = trend.ema_cross_signals(df, ticker)
# df = trend.ema_price_cross_signals(df, ticker)
df = trend.MACD_signals(df, 'AAPL')
print (df.head())

# print (main_df[['MMM close']])

# print (main_df.head(2))

# prof_df = profit_compare(tickers, main_df)
# print (prof_df.head())
# print (prof_df.sum())

# df.to_pickle('stock_dfs/{}.pickle'.format(ticker))

# plotter('MMM', "EMA Price Cross")

# update_df = web.DataReader('TECL', 'iex', '12-31-18', dt.date.today())
# update_df.index = pd.to_datetime(update_df.index)
# update_df = update_df[['close']]
# update_df.columns = ['TECL close']
#
# print (update_df.columns)
# print (update_df.tail())
# print (type(update_df.index))
#
# tecl_df = pd.read_pickle('TECL.pickle')
# print (tecl_df.tail())
# print (type(tecl_df.index))
#
#
# add_df = tecl_df.merge(update_df, how='outer', on='TECL close', left_index=True, right_index=True)
# print (add_df)
