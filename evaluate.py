import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.style as style
from mpl_finance import candlestick_ohlc
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DayLocator, MONDAY
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import math
style.use('seaborn')

def formatting(df):
    df['Profit/Loss Pct'] = df['Profit/Loss Pct'].map('{:,.2f}%'.format)

def pos_val_sell_val(df):

    df['Position Value'] = df['Entry Price']*df['Shares']
    df['Sell Value'] = df['Exit Price']*df['Shares']
    df['Profit/Loss Amt'] = df['Sell Value']-df['Position Value']
    df['Profit/Loss Pct'] = df['Profit/Loss Amt']/df['Position Value'] * 100

def time_period_PL_analysis(df, starttime, endtime=pd.Timestamp('today'), entry=False):
    start = starttime
    end = endtime
    if entry:
        prof = df[(df['Entry Date'] > start) & (df['Entry Date'] < endtime)]['Profit/Loss Amt'].sum()
    else:
        prof = df[(df['Exit Date'] > start) & (df['Exit Date'] < endtime)]['Profit/Loss Amt'].sum()
    return prof

def source_analysis(df, name, starttime = '2015-01-01', endtime = pd.Timestamp('today')):
    start = pd.Timestamp(starttime)
    end = pd.Timestamp(endtime)
    try:
        prof = df[(df['Name'].str.contains(name)) & (df['Exit Date'] >= start) & (df['Exit Date'] <= end)]["Profit/Loss Amt"].sum()
        # prof = df[(df['Entry Date'] > start) & (df['Entry Date'] < endtime)]
        return prof
    except Exception as e:
        print ('Name is not valid, got error: ', e)
        print ('Valid names are: ', df['Name'].unique())

def strategy_analysis(df, plot=False, start='2015-01-01', end=pd.Timestamp('today')):
    strategies = df['Name'].unique()
    values = []
    holdstrats = {}
    for strategy in strategies:

        profit = source_analysis(df, strategy, start, end)
        holdstrats[strategy] = profit
        values.append(profit)
    if plot:
        print (strategies)
        meanval = sum(values)/len(values)
        # values = holdstrat
        plt.bar(strategies,values,)# figsize=(12,8))
        plt.axhline(y=meanval, c='r', label='Average Return: %s'%str(meanval))
        plt.xticks(rotation=90)
        plt.ylabel('Total Return per Strategy')
        plt.xlabel('Strategy')
        plt.title('Return vs Strategy')
        plt.legend()
        plt.tight_layout()
        # ax.bar(holdstrats)
        plt.show()
    return holdstrats

def read_in_doc(docname):
    df = pd.read_csv(docname)
    df = df[['Ticker', 'Source', 'Name', 'Shares', 'L/S', 'Entry Price',
                'Entry Date', 'Exit Price', 'Exit Date']]
    # df['Entry Price'] = df['Entry Price'].str.strip('$').astype(float)
    return df

def plot_trade(buydf, ticker):
    buydf.set_index('Ticker', inplace=True)

    amt = round(buydf.loc[ticker]['Profit/Loss Amt'],2)
    pct = round(buydf.loc[ticker]['Profit/Loss Pct'],2)
    entrydate = date2num(buydf.loc[ticker]['Entry Date'])
    entryprice = buydf.loc[ticker]['Entry Price']
    exitdate = date2num(buydf.loc[ticker]['Exit Date'])
    exitprice = buydf.loc[ticker]['Exit Price']

    xs = [entrydate, exitdate]
    ys = [entryprice, exitprice]
    # print (buydf.head())
    # tickind = buydf.loc[[ticker]]
    # print (tickind)
    pricehist = pd.read_pickle('stock_dfs/%s.pickle'%ticker)
    OHLC = pricehist[['open','high','low','close']]
    volumeData = pricehist[['volume']]
    OHLC['dateCopy'] = OHLC.index
    OHLC['MPLDates'] = OHLC['dateCopy'].apply(lambda date: date2num(date))
    volumeData['dateCopy'] = volumeData.index
    volumeData['MPLDates'] = volumeData['dateCopy'].apply(lambda date: date2num(date))

    f = plt.figure()
    a = plt.subplot2grid((6,4),(0,0), rowspan=5, colspan=4)
    a2 = plt.subplot2grid((6,4),(5,0),sharex=a, rowspan=1, colspan=4)

    cstick = candlestick_ohlc(a, OHLC[['MPLDates','open','high','low','close']].values, colorup='g',)
    a.set_ylabel('Price')
    a2.bar(volumeData['MPLDates'], volumeData['volume'], facecolor='b')
    a2.set_ylabel('Volume')

    a.xaxis.set_major_locator(mticker.MaxNLocator(3))
    a.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%M-%D'))
    plt.setp(a.get_xticklabels(), visible=False)



    a.scatter(xs, ys, s=50)
    print ('Here: ',buydf.loc[ticker]['Profit/Loss Amt'])
    # title = "Trade of "+ticker+ ".  Profit of: "+amt+' which is ',pct,'%'
    title = "Trade of {} for a profit of ${}, which is {}%".format(ticker,amt,pct)
    print (title)
    a.set_title(title)

    plt.show()


df = read_in_doc('closed.csv')
df.dropna(inplace=True)
df['Entry Date'] = pd.to_datetime(df['Entry Date'])
df['Exit Date'] = pd.to_datetime(df['Exit Date'])
pos_val_sell_val(df)
# formatting(df)


print (df.tail())
plot_trade(df, 'TWTR')
# print (df.tail())
# booldf = df['Exit Date'] > '2019-02-01'
# money = df[df['Exit Date'] > '2019-02-01']['Profit/Loss Amt'].sum()

# print (time_period_PL_analysis(df, '2019-02-01'))
# print (source_analysis(df, 'DMACD X', starttime='2019-02-01'))

# eachStrat = df['Name'].unique()
# stratdict = {}
# for strategy in eachStrat:
#     stratdict[strategy] = source_analysis(df, strategy)
# print (stratdict)

# strategy_analysis(df, True)




# print (money)
# print (booldf)
# print (type(df['Entry Date'][0]))
