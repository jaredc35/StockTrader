import pandas as pd
import pandas_datareader as web
import datetime as dt
import pickle
import matplotlib.pyplot as plt
import numpy as np

def get_stock_df(tickers, update=False):
    '''
    tickers
    '''
    start=dt.date(2018,12,24)
    end=dt.date.today()
    all_df = pd.DataFrame()
    good_tickers = []

    for ticker in tickers:
        try:

            df = web.DataReader(ticker, 'iex', start, end)
            # print (df.head())
            df.index = pd.to_datetime(df.index)
            df = df[['close']]
            df.rename(columns={'close':'%s close'%ticker},inplace=True)
            df['%s Returns'%ticker] = df['%s close'%ticker].pct_change(1)
            df['%s Cumulative Returns'%ticker] = np.exp(np.log1p(df['%s Returns'%ticker]).cumsum())
            # print (df.head())
            if all_df.empty:
                all_df = df
            else:
                all_df = all_df.join(df, how='outer')
            good_tickers.append(ticker)
        except:
            print ('Exception Thrown for: ',ticker)
            continue



    return all_df, good_tickers

def run(movers,tickers, best_50 = True, reload=False, plot=False):
    '''
    Determines which things to run
    '''
    if best_50:
        top_picks = movers[-50:]
    else:
        top_picks = movers

    if reload:
        main_df, tickers = get_stock_df(top_picks)
        main_df.to_pickle('bestReturns.pickle')
        with open('usableTickers.pickle','wb') as f:
            pickle.dump(tickers, f)
    else:
        main_df = pd.read_pickle('bestReturns.pickle')
        # with open('usableTickers.pickle','rb') as f:
        #     tickers = pickle.load( f)

    # print (main_df.head())
    # print (main_df.head())
    # main_df.fillna(method='backfill', inplace=True)
    returns_df = main_df[['%s Cumulative Returns'%ticker for ticker in tickers]]
    plt.bar(range(returns_df.loc['2019-05-01'].shape[0]), returns_df.loc['2019-05-01'])
    returns_df.loc['2019-05-01'].plot.bar()
    # print (returns_df.head())

    # returns_df = cum_return_df.transpose()
    returns_df.fillna(0,inplace=True)
    # returns_df.dropna(inplace=True, axis=1, thresh=20)

    # print (returns_df)
    returns_df.sort_values(by='2019-05-01',axis=1, inplace=True)
    print (returns_df.tail())



    print (returns_df.loc['2019-05-01'].describe())
    if plot:
        returns_df.iloc[:,-10:].plot()
        plt.legend()

        plt.show()



if __name__=='__main__':
    total_list = ['CAG', 'ROKU', 'X', 'RIG', 'FDX', 'XPO', 'APA', 'CXO', 'HES', 'TIF', 'SLB', 'ULTA', 'WDC', 'DVN', 'STI', 'ZAYO', 'BBY', 'CCL', 'C', 'KEY', 'PM', 'CFG', 'APC', 'SPOT', 'HBAN', 'PXD', 'HAL', 'MRO', 'RF', 'EOG', 'USB', 'MU', 'GS', 'STZ', 'STT', 'CAH', 'CMA', 'CTL', 'CMG', 'COF', 'SQ', 'PNC', 'BBT', 'OXY', 'CNC', 'WBA', 'UTX', 'EMR', 'AAL', 'LB', 'FITB', 'CVS', 'NXPI', 'AGN', 'GD', 'AAPL', 'AXP', 'WFC', 'AIG', 'UPS', 'AMAT', 'KHC', 'MNST', 'MS', 'BAC', 'NTAP', 'MGM', 'HPE', 'TWTR', 'CI', 'LYB', 'AAP', 'DXC', 'CSX', 'NSC', 'PRU', 'SCHW', 'HPQ', 'JPM', 'ACN', 'NWL', 'M', 'CTSH', 'SYF', 'GRUB', 'LMT', 'MAR', 'XOM', 'UAL', 'PSX', 'RTN', 'URI', 'FCX', 'LUV', 'TGT', 'WP', 'WMB', 'WYNN', 'DAL', 'NOC', 'F', 'PH', 'CVX', 'LRCX', 'BLL', 'BDX', 'FAST', 'BIIB', 'COST', 'DXCM', 'ADSK', 'MPC', 'MCK', 'ADP', 'BK', 'HCA', 'DWDP', 'JCI', 'AABA', 'ETN', 'NVDA', 'EL', 'HON', 'MELI', 'MET', 'TTD', 'ILMN', 'HUM', 'SPG', 'ATVI', 'CELG', 'MO', 'AMD', 'KSS', 'ORCL', 'VLO', 'ANTM', 'ISRG', 'KMI', 'FDC', 'JNJ', 'TJX', 'AMZN', 'SWK', 'LEN', 'EA', 'COP', 'BLK', 'SPGI', 'TRV', 'HLT', 'GE', 'UNH', 'SYK', 'LULU', 'SBUX', 'ICE', 'SWKS', 'V', 'ADI', 'ALGN', 'ADBE', 'MMM', 'SIRI', 'UNP', 'ITW', 'BKNG', 'MXIM', 'TMO', 'TMUS', 'KR', 'BHGE', 'VZ', 'FB', 'CF', 'CHTR', 'DIS', 'WMT', 'MCHP', 'CSCO', 'PGR', 'MA', 'W', 'AMGN', 'A', 'IBM', 'PCG', 'MDLZ', 'BMY', 'INTU', 'GLW', 'EBAY', 'GM', 'K', 'PPL', 'XLNX', 'NFLX', 'TXN', 'DHI', 'SYY', 'GILD', 'TSLA', 'ROST', 'LVS', 'DG', 'TTWO', 'CB', 'BSX', 'WCG', 'MRVL', 'T', 'MSFT', 'HD', 'MDT', 'INTC', 'ORLY', 'DHR', 'PEP', 'BA', 'MCD', 'ARRS', 'ABMD', 'BAX', 'CME', 'CL', 'LIN', 'CAT', 'VMW', 'PFE', 'EW', 'NRG', 'VRTX', 'CCI', 'MRK', 'ABT', 'KO', 'PHM', 'AMT', 'PYPL', 'SO', 'ATHN', 'TWLO', 'SPLK', 'LOW', 'CRM', 'NEE', 'PG', 'DVMT', 'SRE', 'RHT', 'NEM', 'XEL', 'REGN', 'QCOM', 'AZO', 'DE', 'AEP', 'DUK', 'DLTR', 'YUM', 'BURL', 'NOW', 'ED', 'PANW', 'EIX', 'EQT', 'AVGO', 'WDAY', 'TSRO']
    # run(True)
    run(total_list, total_list, best_50=False,reload=False, plot=True)
