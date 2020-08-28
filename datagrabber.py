import trend
import datetime as dt
import os
import pickle
import pandas as pd
import pandas_datareader as web
import quandl
import requests
import bs4 as bs

def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text #Table data, 0th col
        tickers.append(ticker)
    with open('sp500tickers.pickle', 'wb') as f:
        pickle.dump(tickers, f)

    return tickers

def get_iex_data(start=dt.date.today()-dt.timedelta(days=5*365), end=dt.date.today(), reload_sp500=False):
    '''
    Get Data from iex, only allows data from last five years
    but consider...
    ## Once the pickles of all the stocks are made, consider
    updating occasionally and just adding on to each of them. ##
    '''
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open('sp500tickers.pickle', 'rb') as f:
            tickers = pickle.load(f)

    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    for ticker in tickers:
        print (ticker)
        if not os.path.exists('stock_dfs/{}.pickle'.format(ticker)):
            try:
                df = web.DataReader(ticker, 'iex', start, end) # Pulls in data
                df.index = pd.to_datetime(df.index)
                df.to_pickle('stock_dfs/{}.pickle'.format(ticker))
            except:
                continue
        else:
            print ('Already have {}'.format(ticker))

def update_iex_data():
    save_sp500_tickers()
    with open('sp500tickers.pickle', 'rb') as f:
        tickers = pickle.load(f)


    for ticker in tickers:
        try:
            print (ticker)
            original_df = pd.read_pickle('stock_dfs/{}.pickle'.format(ticker))
            original_df.index = pd.to_datetime(original_df.index)
            last_date = original_df.index[-1] #Grabs the last date to add on to

            print ('--------')
            update_df = web.DataReader(ticker, 'iex', last_date, dt.date.today())
            columns = ['open', 'high', 'low', 'close', 'volume']
            df = original_df.merge(update_df, how='outer', on=columns,
                                    left_index=True, right_index=True)
            df.to_pickle('stock_dfs/{}.pickle'.format(ticker))
        except:
            #Some of the stocks from S&P 500 not in IEX
            continue




def get_data_from_alphavantage(intraday = False, reload_sp500 = False):
    """
    Get data from alphavantage, however it is limited to
    five calls per minute so its very difficult to grab data
    on large amounts of data.
    ## Consider coming back to this using datetime to
    throttle requests on alpha_vantage since it also provides
    intraday information ##
    """
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open('sp500tickers.pickle', 'rb') as f:
            tickers = pickle.load(f)

    if not os.path.exists('AV_stock_dfs'):
        os.makedirs('AV_stock_dfs')

    start = dt.datetime(2000,1,1)
    for ticker in tickers:
        if not os.path.exists('AV_stock_dfs/{}.pickle'.format(ticker)):
            if intraday: df = trend.get_intraday_stockdata(ticker, start)
            else: df = trend.get_stockdata(ticker, start)
            df.to_pickle('AV_stock_dfs/{}.pickle'.format(ticker))
        else:
            print ('Already have {}'.format(ticker))

def get_quandl_data(reload_sp500=False):
    '''
    Get the data from the free quandl stocks
    listed in their database
    '''
    api_key = process.env.QUANDL_API

    # if reload_sp500:
    #     tickers = save_sp500_tickers()
    # else:
    #     with open('sp500tickers.pickle', 'rb') as f:
    #         tickers = pickle.load(f)

    if not os.path.exists('Q_stock_dfs'):
        os.makedirs('Q_stock_dfs')
    # start = dt.datetime(1996,1,1)
    tickers = ['HD',]#'DIS', 'MSFT', 'BA', 'MMM', 'PFE', 'NKE', 'JNJ', 'MCD',
            # 'INTC', 'XOM', 'GS', 'JPM', 'AXP', 'V', 'UNH', 'PG', 'GE', 'KO',
            # 'CSCO', 'CVX', 'CAT', 'WMT', 'VZ', 'UTX', 'TRV','AAPL']

    for ticker in tickers:
        if not os.path.exists('Q_stock_dfs/{}.pickle'.format(ticker)):
            df = quandl.get("EOD/%s" % ticker, authtoken="bX_Xcz7AXRHufAerdKB3")
            df = df[['Adj_Close']]
            df.rename(columns = {'Adj_Close': '%s close'% ticker}, inplace=True)
            # print (df.head())
            df.to_pickle('stock_dfs/{}.pickle'.format(ticker))

        else:
            print ('Already have {}'.format(ticker))


if __name__ == '__main__':
    update_iex_data()
