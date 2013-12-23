import numpy as np
import pandas as pd
import math
import VA_PYTHON as va
from VA_PYTHON.simulator.dataengine import *
import VD_DATABASE as vd
from collections import defaultdict
import datetime as dt
from time import strptime
from dateutil import rrule
from dateutil.parser import parse
import types
import ipdb

class portfolioManager(object):


    def __init__(self, simulator):

        self.simulator = simulator

        self.initialcapital = 1000000.0
        self.portfolioSymbol = set()
        self.portfolio = pd.DataFrame(
            dict(time=dt.datetime(1990,1,1),symbol='VSCHON',price=np.zeros(100000),
                 number=np.zeros(100000),direction='long',
                 open = 'open', tradeID = np.zeros(100000),
                 cash=np.zeros(100000),value=np.zeros(100000)),
            columns = ['time', 'tradeID', 'symbol','price','number','direction','open','cash','value'])
        self.tradeIndex = 0
        self.tradeVerbose = True

    def setcapital(self,value):
        '''
        set the initial value of simulation value
        defaul to be 1 million
        '''
        self.initialcapital = value

    def getLatestPortfolio(self):
        latestIndex = self.tradeIndex - 1
        return self.portfolio.ix[latestIndex]

    def getLatestLongPosition(self, symbol):
        point = self.getLatestPortfolio()
        if symbol in self.portfolioSymbol:
            return point[(symbol + '-long')]
        else:
            return 0

    def getLatestShortPosition(self, symbol):
        point = self.getLatestPortfolio()
        if symbol in self.portfolioSymbol:
            return point[(symbol + '-short')]
        else:
            return 0

    def getLatestNetPosition(self, symbol):
        netPosition = self.getLatestLongPosition(symbol) - self.getLatestshortPosition(symbol)
        return netPosition

    def getLatestCash(self):
        return self.getLatestPortfolio['cash']

    def getLatestWealth(self):
        return self.getLatestPortfolio['value']

    def updatePortfolio(self,trade):
        '''
        update portfolio based on new trades
        '''

        if self.tradeIndex%100000 == 0 and self.tradeIndex!=0:
            portfolio_copy = self.portfolio[:100000].copy()
            portfolio_copy['price'] = dt.datetime(1990,1,1)
            portfolio_copy['tradeID'] = 0
            portfolio_copy['symbol'] = 'VSCHON'
            portfolio_copy['price'] = 0.0
            portfolio_copy['number'] = 0.0
            portfolio_copy['direction'] = 'long'
            portfolio_copy['open'] = 'open'
            portfolio_copy['cash'] = 0.0
            portfolio_copy['value'] = 0.0
            self.portfolio = pd.concat([self.portfolio,portfolio_copy],ignore_index=True)

        time = trade['time']
        symbol = trade['symbol']
        price = trade['price']
        direction = trade['direction']
        number = trade['number']
        open = trade['open']
        tradeID = trade['tradeID']

        mark = 0.0
        if direction == 'long':
            mark = 1.0
        elif direction == 'short':
            mark = -1.0

        #if symbol not in portfolio, add threee cols - long,short,price
        if symbol not in self.portfolioSymbol:
            self.portfolio[symbol + '-long'] = np.zeros(self.portfolio.shape[0])
            self.portfolio[symbol + '-short'] = np.zeros(self.portfolio.shape[0])
            self.portfolio[symbol + '-price'] = np.zeros(self.portfolio.shape[0])
            self.portfolioSymbol.add(symbol)

        #ipdb.set_trace()

        if self.tradeIndex == 0:
            #special case for first trade
            #update cash
            self.portfolio['cash'][self.tradeIndex] = self.initialcapital - mark*number*price

            #update traded symbol number
            if open == 'open':
                if direction == 'long':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = number
                elif direction == 'short':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = number
            elif open == 'close':
                if direction == 'short':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = -number
                elif direction == 'long':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = -number
        else:
            #for 2nd and after trades
            #update cash
            self.portfolio.iloc[self.tradeIndex] = self.portfolio.ix[self.tradeIndex-1]
            #copy the data of last trade into current line
            self.portfolio['cash'][self.tradeIndex] = self.portfolio['cash'][self.tradeIndex-1] - mark*number*price

            #update traded symbol number
            if open == 'open':
                if direction == 'long':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = number + self.portfolio.ix[self.tradeIndex][symbol + '-long']
                elif direction == 'short':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = number + self.portfolio.ix[self.tradeIndex][symbol + '-short']
            elif open == 'close':
                if direction == 'short':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = -number + self.portfolio.ix[self.tradeIndex][symbol + '-long']
                elif direction == 'long':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = -number + self.portfolio.ix[self.tradeIndex][symbol + '-short']

        #update traded symbol price
        self.portfolio[symbol + '-price'][self.tradeIndex] = price

        #update non-traded symbol price
        #get all symbols that are not traded
        tempset = set()
        tempset.add(symbol)
        tempsym = self.portfolioSymbol.difference(tempset)

        for sym in tempsym:
            tempprice =  self.simulator.dataEngine.queryPrice(sym, time)
            self.portfolio[sym + '-price'][self.tradeIndex] = tempprice

        #update portfolio value
        sum = 0.0
        for sym in self.portfolioSymbol:
            symnumber = self.portfolio[sym + '-long'][self.tradeIndex] - self.portfolio[sym + '-short'][self.tradeIndex]
            sum += symnumber * self.portfolio[sym + '-price'][self.tradeIndex]
        self.portfolio['value'][self.tradeIndex] = sum + self.portfolio['cash'][self.tradeIndex]

        #update transaction time, symbol,price, number, direction and open
        self.portfolio['time'][self.tradeIndex] = time
        self.portfolio['symbol'][self.tradeIndex] = symbol
        self.portfolio['price'][self.tradeIndex] = price
        self.portfolio['number'][self.tradeIndex] = number
        self.portfolio['direction'][self.tradeIndex] = direction
        self.portfolio['open'][self.tradeIndex] = open
        self.portfolio['tradeID'][self.tradeIndex] = tradeID

        if self.tradeVerbose == True:
            self.__printTrade(trade)
            print 'Portfolio Value: ' + str(self.portfolio['value'][self.tradeIndex]) + '\n'
        self.tradeIndex += 1

    def __printTrade(self,trade):
        print trade['time'].strftime(format = "%Y%m%d %H:%M:%S.%f") + " ",
        print "%s %s %d %s at %f" % (trade['open'], trade['direction'], trade['number'], trade['symbol'], trade['price'])

    def setTradeVerbose(self, tradeVerbose):
        self.tradeVerbose = tradeVerbose


    def summarize(self):
        self.portfolio = self.portfolio[self.portfolio['price']!=0]
        self.__portfolioAnalyzer()

    def __tradeAnalyzer(self):
        pass

    def __portfolioAnalyzer(self):
        '''
        evaluate the performance of trader
        '''

        '''
        ALGO:
            For general-daily analysis
            cut un-filled entries
            divide the portfolio into cycles
            suppose each cycle corresponds to each day
        '''

        result = self.portfolio
        result.index = result['time']
        cycles = self.simulator.cycleManager.cycles
        initialValue = self.initialcapital
        #cut the result based on cycles
        divisions = [result[va.utils.utils.datetime2str(cycle['beginTime']):va.utils.utils.datetime2str(cycle['endTime'])] for cycle in cycles]

        #for per cycle value
        summary_list = []
        for i in range(len(cycles)):
            temp = {}
            element = divisions[i]
            cycle = cycles[i]
            if element.shape[0] == 0:
                pass
            else:
                #set time
                temp['beginTime'] = cycle['beginTime']
                temp['beginDate'] = cycle['beginDate']
                temp['endTime'] = cycle['endTime']
                temp['endDate'] = cycle['endDate']

                #fill portfolio value for each date
                temp['value'] = element['value'].ix[-1]
            summary_list.append(temp)

        summary_df = pd.DataFrame(summary_list,
                                  columns = ['beginTime','value','beginDate','endTime','endDate'])


        #drop empty entries
        summary_df = summary_df.dropna()
        value = summary_df['value'].values
        aug_value = np.insert(value,0,initialValue)
        daily_return = aug_value[1:] / aug_value[:-1] - 1

        #cumulative return
        cum_return = aug_value/aug_value[0] - 1
        cum_return = np.delete(cum_return,0)

        #sharpe ratio
        avg_return = np.average(daily_return)
        std_return = np.std(daily_return)
        sharpe = math.sqrt(250) * avg_return / std_return

        #drawdown and drawdown duration
        drawdown = np.zeros(value.shape)
        drawdownDuration = np.zeros(value.shape)
        highwatermark = np.zeros(value.shape)

        for t in range(value.shape[0]) :
            highwatermark[t] = (max(highwatermark[t-1], cum_return[t]))
            drawdown[t]= - (highwatermark[t]-cum_return[t])
            drawdownDuration[t]= (0 if drawdown[t] == 0 else drawdownDuration[t-1]+1)

        summary_df['daily_return'] = daily_return
        summary_df['drawdown'] = drawdown
        summary_df['drawdown_duration'] = drawdownDuration

        maxdrawdown = np.argmin(drawdown)
        maxdrawdown_duration = np.argmax(drawdownDuration)

        return summary_df

        #General analyzer
        #maximum winning days

        #Per trade analyzer
        #winning rate: win#/trade#


