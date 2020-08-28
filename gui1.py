import matplotlib
matplotlib.use("TkAgg") #Allows to change back end
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from mpl_finance import candlestick_ohlc
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DayLocator, MONDAY
from matplotlib import style
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

from alpha_vantage.timeseries import TimeSeries

import tkinter as tk
from tkinter import ttk

import urllib
import json

import pandas as pd
import pandas_datareader as web
import numpy as np


LARGE_FONT = ('Verdana', 12)
NORM_FONT = ('Verdana', 10)
SMALL_FONT = ('Verdana', 8)
style.use('ggplot')

f = plt.figure() #Simple Figure
# a = f.add_subplot(111) #1x1 and 1st chart
# fig, ax = plt.subplots(dpi=100)
# fig.subplots_adjust(bottom=0.2)
# mondays = WeekdayLocator(MONDAY)
# alldays = DayLocator()
# weekFormatter = DateFormatter('%b %d')
# dayFormatter = DateFormatter('%d')
#
# a.xaxis.set_major_locator(mondays)
# a.xaxis.set_minor_locator(alldays)
# a.xaxis.set_major_formatter(weekFormatter)

exchange = 'IEX'
forceCounter = 10**6
programName = 'Stock'

resampleSize = 'D'
dataPace = '7d'
candlewidth = 0.008
paneCount = 1
topIndicator = 'none'
bottomIndicator = 'none'
middleIndicator = 'none'
tickername = 'AAPL'
EMAs = []
SMAs = []
chartLoad = True

def loadChart(run):
    global chartLoad

    if run == 'start':chartLoad=True
    elif run=='stop':chartLoad=False

def tutorial():

    # def leavemini(what):
    #     what.destroy()
    def page2():
        tut.destroy()
        tut2 = tk.Tk()

        def page3():
            tut2.destroy()
            tut3 = tk.Tk()
            tut3.wm_title('Part 3!')
            label = ttk.Label(tut3, text='Part 3', font=NORM_FONT)
            label.pack(side='top', fill='x', pady=10)
            B1 = ttk.Button(tut3, text='Done!', command=tut3.destroy)
            B1.pack()
            tut3.mainloop()

        tut2.wm_title('Part 2!')
        label = ttk.Label(tut2, text='Part 2', font=NORM_FONT)
        label.pack(side='top', fill='x', pady=10)
        B1 = ttk.Button(tut2, text='Done!', command=page3)
        B1.pack()
        tut2.mainloop()

    tut = tk.Tk()
    tut.wm_title('Tutorial!')
    label = ttk.Label(tut, text='What do you need help with', font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)

    B1 = ttk.Button(tut, text='Overview of Application', command=page2)
    B1.pack()
    B2 = ttk.Button(tut, text='How do I trade?', command=lambda:popupmsg('Not done'))
    B2.pack()
    B3 = ttk.Button(tut, text='Indicator Questions/Help', command=lambda:popupmsg('Not done'))
    B3.pack()

    tut.mainloop()

def addTopIndicator(what):
    global topIndicator
    global forceCounter

    if dataPace == 'tick':
        popupmsg('Indicators in Tick Data not available')
    elif what == 'none':
        topIndicator = what
        forceCounter = 10**6
    elif what == 'rsi':
        rsiQ = tk.Tk()
        rsiQ.wm_title("Periods?")
        label = ttk.Label(rsiQ, text='Choose how many periods for RSI to consider.')
        label.pack(side='top', fill='x', pady=10)

        e = ttk.Entry(rsiQ)
        e.insert(0,14) # Insert 14 at 0 index
        e.pack()
        e.focus_set()
        def callback():
            global topIndicator
            global forceCounter
            periods = (e.get())
            group = []
            group.append('rsi')
            group.append(periods)

            topIndicator = group
            forceCounter = 10**6
            print ('Set top Indicator to', group)
            rsiQ.destroy()

        b = ttk.Button(rsiQ, text='Submit', width=10, command=callback)
        b.pack()
        tk.mainloop()

    elif what == 'macd':
        # global topIndicator
        # global forceCounter
        topIndicator = 'macd'
        forceCounter = 10**6

def addMiddleIndicator(what):
    global middleIndicator
    global forceCounter

    if dataPace == 'tick':
        popupmsg('Indicators in Tick Data not available')

    if what != 'none':
        if middleIndicator == 'none':
            if what == 'sma':
                midIQ = tk.Tk()
                midIQ.wm_title('Periods')
                label=ttk.Label(midIQ, text='Choose how many periods for SMA')
                label.pack(side='top', fill='x', pady=10)
                e = ttk.Entry(midIQ)
                e.insert(0,13)
                e.pack()
                e.focus_set()

                def callback():
                    global middleIndicator
                    global forceCounter

                    middleIndicator = []
                    periods = (e.get())
                    group = []
                    group.append('sma')
                    group.append(int(periods))
                    middleIndicator.append(group)
                    forceCounter = 10**6
                    print ('Middle Indicator set to:', middleIndicator)
                    midIQ.destroy()
                b = ttk.Button(midIQ, text='Submit', width=10, command=callback)
                b.pack()
                tk.mainloop()

            if what == 'ema':
                midIQ = tk.Tk()
                midIQ.wm_title('Periods')
                label=ttk.Label(midIQ, text='Choose how many periods for EMA')
                label.pack(side='top', fill='x', pady=10)
                e = ttk.Entry(midIQ)
                e.insert(0,13)
                e.pack()
                e.focus_set()

                def callback():
                    global middleIndicator
                    global forceCounter

                    middleIndicator = []
                    periods = (e.get())
                    group = []
                    group.append('ema')
                    group.append(int(periods))
                    middleIndicator.append(group)
                    forceCounter = 10**6
                    print ('Middle Indicator set to:', middleIndicator)
                    midIQ.destroy()
                b = ttk.Button(midIQ, text='Submit', width=10, command=callback)
                b.pack()
                tk.mainloop()

        else:
            # Middle indicator has already been established
            if what == 'sma':
                midIQ = tk.Tk()
                midIQ.wm_title('Periods')
                label=ttk.Label(midIQ, text='Choose how many periods for SMA')
                label.pack(side='top', fill='x', pady=10)
                e = ttk.Entry(midIQ)
                e.insert(0,13)
                e.pack()
                e.focus_set()

                def callback():
                    global middleIndicator
                    global forceCounter

                    periods = (e.get())
                    group = []
                    group.append('sma')
                    group.append(int(periods))
                    middleIndicator.append(group)
                    forceCounter = 10**6
                    print ('Middle Indicator set to:', middleIndicator)
                    midIQ.destroy()
                b = ttk.Button(midIQ, text='Submit', width=10, command =callback)
                b.pack()
                tk.mainloop()
            if what == 'ema':
                midIQ = tk.Tk()
                midIQ.wm_title('Periods')
                label=ttk.Label(midIQ, text='Choose how many periods for EMA')
                label.pack(side='top', fill='x', pady=10)
                e = ttk.Entry(midIQ)
                e.insert(0,13)
                e.pack()
                e.focus_set()

                def callback():
                    global middleIndicator
                    global forceCounter

                    periods = (e.get())
                    group = []
                    group.append('ema')
                    group.append(int(periods))
                    middleIndicator.append(group)
                    forceCounter = 10**6
                    print ('Middle Indicator set to:', middleIndicator)
                    midIQ.destroy()
                b = ttk.Button(midIQ, text='Submit', width=10, command = callback)
                b.pack()
                tk.mainloop()

    else:
        middleIndicator = 'none'
        forceCounter = 10**6
def addBottomIndicator(what):
    global bottomIndicator
    global forceCounter

    if dataPace == 'tick':
        popupmsg('Indicators in Tick Data not available')
    elif what == 'none':
        bottomIndicator = what
        forceCounter = 10**6
    elif what == 'rsi':
        rsiQ = tk.Tk()
        rsiQ.wm_title("Periods?")
        label = ttk.Label(rsiQ, text='Choose how many periods for RSI to consider.')
        label.pack(side='top', fill='x', pady=10)

        e = ttk.Entry(rsiQ)
        e.insert(0,14) # Insert 14 at 0 index
        e.pack()
        e.focus_set()
        def callback():
            global bottomIndicator
            global forceCounter
            periods = (e.get())
            group = []
            group.append('rsi')
            group.append(periods)

            bottomIndicator = group
            forceCounter = 10**6
            print ('Set bottom indicator to', group)
            rsiQ.destroy()

        b = ttk.Button(rsiQ, text='Submit', width=10, command=callback)
        b.pack()
        tk.mainloop()

    elif what == 'macd':
        # global topIndicator
        # global forceCounter
        bottomIndicator = 'macd'
        forceCounter = 10**6


def changeTimeFrame(tf):
    global dataPace
    global forceCounter

    if tf =='7d' and resampleSize == '1Min':
        popupmsg('Too much data chosen, choose smaller time frame or higher OHLC interval')
    else:
        dataPace = tf
        forceCounter = 10**6

def changeSampleSize(size, width):
    global resampleSize
    global forceCounter
    global candlewidth

    if dataPace =='7d' and resampleSize == '1Min':
        popupmsg('Too much data chosen, choose smaller time frame or higher OHLC interval')

    elif dataPace == 'tick':
        popupmsg('Currently viewing tick data, not OHLC')
    else:
        resampleSize = size
        forceCounter = 10**6
        candlewidth = width

def changeExchange(toWhat, pn):
    global exchange
    global forceCounter
    global programName

    exchange = toWhat
    programName = pn
    forceCounter = 10**6

def changeStock():
    changewindow = tk.Tk()
    changewindow.wm_title('Stock Choice')
    label = ttk.Label(changewindow, text='Choose a stock')
    label.pack(side='top', fill='x', pady=10)
    e = ttk.Entry(changewindow)
    e.insert(0, 'AAPL')
    e.pack()
    e.focus_set()
    def callback():
        global tickername
        tickername = e.get()
        forceCounter =10**6
        print ('Stock set to: ',tickername)
        changewindow.destroy()
    # forceCounter = 100
    b = ttk.Button(changewindow, text='Submit', width=10, command=callback)
    b.pack()
    tk.mainloop()

def popupmsg(msg):
    popup = tk.Tk()

    def leavemini():
        popup.destroy()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10, padx=10)
    B1 = ttk.Button(popup, text='Okay', command=leavemini)
    B1.pack()
    popup.mainloop()

def animate(i): #i is interval
    global refreshRate
    global forceCounter
    global tickername

    def rsiIndicator(priceData, location='top'):
        if location == 'top':
            values = {'key':1,'prices':priceData,'periods':topIndicator[1]}
        if location == 'bottom':
            values = {'key':1,'prices':priceData,'periods':bottomIndicator[1]}
    def computeMACD(priceOHLC, slow=26, fast=13, location='bottom'):
        fastema = priceOHLC['close'].ewm(span=fast, adjust=False).mean()
        slowema = priceOHLC['close'].ewm(span=slow, adjust=False).mean()
        MACDLine = fastema-slowema
        signalLine = MACDLine.ewm(span=9, adjust=False).mean()
        if location == 'top':
            try:
                a0.plot(priceOHLC['MPLDates'], MACDLine, c='g', ls='--', label="MACD Line")
                a0.plot(priceOHLC['MPLDates'], signalLine, c='r', label='Signal Line')
                a0.fill_between(priceOHLC['MPLDates'], MACDLine-signalLine, 0, alpha=0.5, facecolor='b')
                label = 'MACD'
                a0.set_ylabel(label)
            except Exception as e:
                print (str(e))
                topIndicator = 'None'
        if location == 'bottom':
            try:
                a3.plot(priceOHLC['MPLDates'], MACDLine, c='g', ls='--', label="MACD Line")
                a3.plot(priceOHLC['MPLDates'], signalLine, c='r', label='Signal Line')
                a3.fill_between(priceOHLC['MPLDates'], MACDLine-signalLine, 0, alpha=0.5, facecolor='b')
                label = 'MACD'
                a3.set_ylabel(label)
            except Exception as e:
                print (str(e))
                bottomIndicator = 'None'




    if chartLoad:
        if paneCount == 1:
            try:
                if forceCounter > 12:
                # try:

                    if topIndicator != 'none' and bottomIndicator != 'none':
                        # Main Graph
                        a = plt.subplot2grid((6,4), (1,0), rowspan=3, colspan=4)
                        # Volume
                        a2 = plt.subplot2grid((6,4), (4,0), sharex = a, rowspan=1, colspan=4)
                        # Bottom Indicator
                        a3 = plt.subplot2grid((6,4), (5,0),sharex = a, rowspan=1, colspan=4)
                        # Top Inidicator
                        a0 = plt.subplot2grid((6,4), (0,0),sharex = a, rowspan=1, colspan=4)
                    elif topIndicator != 'none':
                        # Main Graph
                        a = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4)
                        # Volume
                        a2 = plt.subplot2grid((6,4), (5,0), sharex = a, rowspan=1, colspan=4)
                        # Top Inidicator
                        a0 = plt.subplot2grid((6,4), (0,0),sharex = a, rowspan=1, colspan=4)
                    elif bottomIndicator != 'none':
                        # Main Graph
                        a = plt.subplot2grid((6,4), (0,0), rowspan=4, colspan=4)
                        # Volume
                        a2 = plt.subplot2grid((6,4), (4,0), sharex = a, rowspan=1, colspan=4)
                        # Bottom Indicator
                        a3 = plt.subplot2grid((6,4), (5,0),sharex = a, rowspan=1, colspan=4)
                    else:
                        # Main Graph
                        a = plt.subplot2grid((6,4), (0,0), rowspan=5, colspan=4)
                        # Volume
                        a2 = plt.subplot2grid((6,4), (5,0), sharex = a, rowspan=1, colspan=4)

                    data = pd.read_pickle('stock_dfs/%s.pickle'%tickername)
                    data_reset = data.reset_index()
                    # data_reset['date_ax'] = data_reset['date'].apply(lambda date: date2num(date))

                    if resampleSize == 'D':
                        OHLC = data[['open','high','low','close']]
                        volumeData = data[['volume']]
                    else:
                        OHLC = data['close'].resample(resampleSize).ohlc()
                        OHLC.dropna(inplace=True)
                        volumeData = data[['volume']].resample(resampleSize).sum()

                    # print (volumeData.head())
                    OHLC['dateCopy'] = OHLC.index
                    OHLC['MPLDates'] = OHLC['dateCopy'].apply(lambda date: date2num(date))
                    volumeData['dateCopy'] = volumeData.index
                    volumeData['MPLDates'] = volumeData['dateCopy'].apply(lambda date: date2num(date))
                    # print (OHLC.head())

                    a.clear()
                    # dates = OHLC['MPLDates'].tolist()
                    # volumeData = data['volume'].tolist()



                    if middleIndicator != 'none':
                        for eachMA in middleIndicator:
                            # ewma = pd.stats.moments.ewma
                            if eachMA[0] =='sma':
                                # OHLC['close'].rolling(eachMA[1]).mean().plot(ax=a)
                                # sma = pd.rolling_mean(OHLC['close'], eachMA[1])
                                label = str(eachMA[1])+" SMA"
                                sma = OHLC['close'].rolling(eachMA[1]).mean()
                                a.plot(OHLC['MPLDates'], sma, label=label)
                            if eachMA[0] == 'ema':
                                # ema = pd.rolling_mean(OHLC['close'], eachMA[1])
                                # ewma = pd.stats.moments.ewma
                                label = str(eachMA[1])+" EMA"
                                ema = OHLC['close'].ewm(span=eachMA[1], adjust=False).mean()
                                # a.plot(ax=a,label=label)
                                a.plot(OHLC['MPLDates'], ema, label=label)
                        a.legend()

                    if topIndicator == 'rsi':
                        rsiIndicator(OHLC, 'top')
                    elif topIndicator == 'macd':
                        try:
                            computeMACD(OHLC, location='top')
                        except Exception as e:
                            print ('here')
                            print (str(e))

                    if bottomIndicator == 'rsi':
                        rsiIndicator(OHLC, 'bottom')
                    elif bottomIndicator == 'macd':
                        try:
                            computeMACD(OHLC, location='bottom')
                        except Exception as e:
                            print (str(e))

                    cstick = candlestick_ohlc(a, OHLC[['MPLDates','open','high','low','close']].values, colorup='g',width=candlewidth,)
                    a.set_ylabel('Price')
                    a2.bar(volumeData['MPLDates'], volumeData['volume'], facecolor='b')
                    a2.set_ylabel('Volume')

                    a.xaxis.set_major_locator(mticker.MaxNLocator(3))
                    a.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%M-%D'))
                    plt.setp(a.get_xticklabels(), visible=False)

                    if topIndicator != 'none':
                        plt.setp(a0.get_xticklabels(), visible=False)
                    if bottomIndicator != 'none':
                        plt.setp(a3.get_xticklabels(), visible=False)

                    x = len(OHLC['close'])-1  #Element ID of last element (to get last price)
                    if dataPace=='W':
                        title = exchange+ "1 Week Data with "+resampleSize+" Bars\nLast Price: "+str(OHLC['close'][x])
                    if dataPace=='M':
                        title = exchange+ "1 Month Data with "+resampleSize+" Bars\nLast Price: "+str(OHLC['close'][x])
                    else:
                        title = tickername

                    if topIndicator != 'none':
                        a0.set_title(title)
                    else: a.set_title(title)
                    print ('new Graph')
                    forceCounter = 0


                else:
                    forceCounter += 1
            except Exception as e:
                    print ('Failed in the non-tick animate: ',str(e))
                    forceCounter = 10**6



class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):


        tk.Tk.__init__(self, *args, **kwargs)


        tk.Tk.wm_title(self, "BTC GUI") #Add title to window

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0) # Tearoff allows you to make it its own window
        filemenu.add_command(label='Save settings', command = lambda: popupmsg('Not Supported just yet'))
        filemenu.add_separator() # Adds a dividor to make more visually appealing
        filemenu.add_command(label='Exit', command=quit)
        menubar.add_cascade(label='File', menu=filemenu)

        exchangeChoice = tk.Menu(menubar,tearoff=1)
        exchangeChoice.add_command(label='IEX',
                                command=lambda: changeExchange('IEX', "IEX"))
        exchangeChoice.add_command(label='Alpha Vantage',
                                command=lambda: changeExchange('Alpha Vantage', "alpha_vantage"))
        exchangeChoice.add_command(label='Robinhood',
                                command=lambda: changeExchange('Robinhood', "robinhood"))
        exchangeChoice.add_command(label='ThinkorSwim',
                                command=lambda: changeExchange('ThinkorSwim', "tos"))
        menubar.add_cascade(label='Exchange', menu=exchangeChoice)

        stockChoice = tk.Menu(menubar, tearoff=1)
        stockChoice.add_command(label='Change Stock', command = lambda: changeStock())
        menubar.add_cascade(label='Stock Choice', menu=stockChoice)

        dataTF = tk.Menu(menubar, tearoff=1)
        dataTF.add_command(label= '1 Week',
                            command = lambda: changeTimeFrame('1w'))
        dataTF.add_command(label= '1 Month',
                            command = lambda: changeTimeFrame('1m'))
        dataTF.add_command(label= '3 Months',
                            command = lambda: changeTimeFrame('3m'))
        dataTF.add_command(label= '6 Months',
                            command = lambda: changeTimeFrame('6m'))
        dataTF.add_command(label= '1 Year',
                            command = lambda: changeTimeFrame('1y'))
        dataTF.add_command(label= '3 Years',
                            command = lambda: changeTimeFrame('3y'))
        dataTF.add_command(label= '5 Years',
                            command = lambda: changeTimeFrame('5y'))
        dataTF.add_command(label= '6 Months',
                            command = lambda: changeTimeFrame('max'))
        menubar.add_cascade(label='Data Time Frame', menu=dataTF)

        OHLCI = tk.Menu(menubar,tearoff=1)
        OHLCI.add_command(label= '1 Day',
                            command = lambda: changeSampleSize('D', 5))
        OHLCI.add_command(label= '1 Week',
                            command = lambda: changeSampleSize('W',8))
        OHLCI.add_command(label= '1 Month',
                            command = lambda: changeSampleSize('M',16))

        menubar.add_cascade(label='OHLC Interval', menu=OHLCI)

        topIndi = tk.Menu(menubar, tearoff=1)
        topIndi.add_command(label='None',
                                    command=lambda:addTopIndicator('none'))
        topIndi.add_command(label='RSI',
                                    command=lambda:addTopIndicator('rsi'))
        topIndi.add_command(label='MACD',
                                    command=lambda:addTopIndicator('macd'))
        menubar.add_cascade(label='Top Indicator', menu=topIndi)

        mainI = tk.Menu(menubar, tearoff=1)
        mainI.add_command(label='None',
                                    command=lambda:addMiddleIndicator('none'))
        mainI.add_command(label='SMA',
                                    command=lambda:addMiddleIndicator('sma'))
        mainI.add_command(label='EMA',
                                    command=lambda:addMiddleIndicator('ema'))
        menubar.add_cascade(label='Main/Middle Indicator', menu=mainI)

        bottomIndi = tk.Menu(menubar, tearoff=1)
        bottomIndi.add_command(label='None',
                                    command=lambda:addBottomIndicator('none'))
        bottomIndi.add_command(label='RSI',
                                    command=lambda:addBottomIndicator('rsi'))
        bottomIndi.add_command(label='MACD',
                                    command=lambda:addBottomIndicator('macd'))
        menubar.add_cascade(label='Bottom Indicator', menu=bottomIndi)

        tradeButton = tk.Menu(menubar, tearoff=1)
        tradeButton.add_command(label='Manual Trading',
                                    command = lambda:popupmsg('This is not live yet'))
        tradeButton.add_command(label='Automated Trading',
                                    command = lambda:popupmsg('This is not live yet'))

        tradeButton.add_separator()
        tradeButton.add_command(label='Quick Buy',
                                    command = lambda:popupmsg('This is not live yet'))
        tradeButton.add_command(label='Quick Sell',
                                    command = lambda:popupmsg('This is not live yet'))

        tradeButton.add_separator()
        tradeButton.add_command(label='Set-up Quick Buy/Sell',
                                    command = lambda:popupmsg('This is not live yet'))
        menubar.add_cascade(label="Trading", menu=tradeButton)

        startStop = tk.Menu(menubar, tearoff=1)
        startStop.add_command(label='Resume',
                                command=lambda: loadChart('start'))
        startStop.add_command(label='Pause',
                                command=lambda: loadChart('stop'))
        menubar.add_cascade(label='Resume/Pause client', menu=startStop)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='Tutorial',
                                command=tutorial)
        menubar.add_cascade(label='Help', menu=helpmenu)

        tk.Tk.config(self,menu=menubar)

        self.frames = dict() #Dict of all the frames in the program

        for F in (StartPage, PageOne, Stock_Page):
            frame = F(container, self) #Make your start page
            self.frames[F] = frame
            frame.grid(row=0,column=0, sticky='nsew') #stretches North, south, east, west

        tk.Tk.iconbitmap(self, default='stock.ico') #Must be ico image
        self.show_frame(StartPage)


    def show_frame(self, cont):
        frame = self.frames[cont] #Calls from dict of frames
        frame.tkraise() #raises it to the front


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text='''ALPHA Stock Trading Application, use
        at your own risk.  There is not promise of warranty''',
                            font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self,text='Agree',
                            command=lambda: controller.show_frame(Stock_Page))
        button1.pack() #Throw the button on the page
        button2 = ttk.Button(self,text='Disagree',
                            command=quit)
        button2.pack() #Throw the button on the page


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text='Page One', font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        button1 = ttk.Button(self,text='Back to Home',
                            command=lambda: controller.show_frame(StartPage))
        button1.pack() #Throw the button on the page

class Stock_Page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text='Graph Page', font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        button1 = ttk.Button(self,text='Back to Home',
                            command=lambda: controller.show_frame(StartPage))
        button1.pack() #Throw the button on the page

        canvas = FigureCanvasTkAgg(f, self)
        # canvas.show() #Works without this line...
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True) #Pack in the widget (could use .grid())
        toolbar = NavigationToolbar2Tk(canvas, self)

        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



app = SeaofBTCapp()
app.geometry('1080x720')
ani = animation.FuncAnimation(f, animate, interval=2000) #Interval in milliseconds

app.mainloop()
