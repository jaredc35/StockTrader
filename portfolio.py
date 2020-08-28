from scipy.optimize import minimize
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import pickle
from itertools import combinations


def get_ret_vol_ser(weights):
    """
    Helper Function which returns a
    np array of returns, volatility, and SR
    """
    weights = np.array(weights)
    ret = np.sum(log_returns.mean()*weights)*252
    vol = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov()*252, weights)))
    sr = ret/vol
    return np.array([ret,vol,sr])

def neg_sharpe(weights):
    """
    Use this function to find the negative sharpe ratio.
    We minimize the negative sharpe to find the max positive sharpe
    """
    return get_ret_vol_ser(weights)[2]*-1

def check_sum(weights):
    """
    Constraint function for Scipy.Optimize
    Returns 0 if sum of weights is 0 (what we want)
    """
    return np.sum(weights)-1

def run_optimization(numstocks, log_returns):
    cons = ({'type':'eq', 'fun':check_sum})
    bounds = tuple([(0,1) for i in range(numstocks)])
    initguess = [1/numstocks]*numstocks

    opt_results = minimize(neg_sharpe, initguess, method="SLSQP",
                            bounds=bounds, constraints=cons)

    return opt.x

def run_monte_simulation(log_ret, num_ports=5000, plot=False):
    num_ports = 5000
    num_stocks = len(log_ret.columns)
    all_weights = np.zeros((num_ports, num_stocks))
    ret_arr = np.zeros(num_ports)
    vol_arr = np.zeros(num_ports)
    sharpe_arr = np.zeros(num_ports)

    for ind in range(num_ports):
        weights = np.array(np.random.random(num_stocks))
        weights = weights/np.sum(weights)
        # Save Weights
        all_weights[ind,:] = weights
        #Expected Return
        ret_arr[ind] = np.sum((log_ret.mean() * weights) * 252)
        # Expected Volatility
        vol_arr[ind] = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov()*252, weights))) #Doing this way because more efficient (linear alg.)
        # Sharpe Ratio
        sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]

    max_SR = sharpe_arr.max()
    max_SR_index = sharpe_arr.argmax()
    best_weights = all_weights[max_SR_index, :]

    if plot:
        max_sr_ret = ret_arr[max_SR_index]
        max_sr_vol = vol_arr[max_SR_index]

        plt.figure(figsize=(12,8))
        plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='plasma')
        plt.colorbar(label='Sharpe Ratio')
        plt.xlabel('Volatility')
        plt.ylabel('Return')

        plt.scatter(max_sr_vol, max_sr_ret, c='r', s=50, edgecolor='k')
        plt.show()

    return (best_weights, max_SR)



def port_allocation(tickers, plot=False):
    """
    This function takes in a list of stocks
    and finds the optimimum portfolio allocation
    """
    main_df = pd.DataFrame()
    numstocks = len(tickers)

    for ticker in tickers:
        try:
            df = pd.read_pickle('stock_dfs/%s.pickle' % ticker)
            df = df[['close']]
            df.rename(columns={'close':'%s close'%ticker}, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df,how='outer')
        except:
            continue

    log_ret = np.log(main_df/main_df.shift(1)) #Find the log return (Normalized)
    # print (log_ret.head())
    weights, SR = run_monte_simulation(log_ret, plot)
    print (weights, SR)

    # run_optimization(numstocks, log_ret)
    return log_ret

# def combinations_of_stocks(all_stocks,num):
#     return list(combinations(all_stocks[:25],num))



# with open('sp500tickers.pickle', 'rb') as f:
#     test = pickle.load(f)

# print (len(combinations_of_stocks(test,5)))
# print (test)
# rand_port = random.sample(test, 10)
#
# df = port_allocation(rand_port, True)
# print (df.head())
