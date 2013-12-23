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

def timeunitparse(timeunit):
    for i in timeunit:
        try:
            int(i)
        except ValueError:
            [value,unit] = timeunit.split(i)
            unit = i + unit
            return (int(value),unit)


class simOrder(object):

    def __init__(self, orderID, time, direction, open,
                 symbol, orderType, number,
                 limitPrice=0, tradeID = 0):
        '''
        tradeID:        trade ID
        orderID:             order ID
        time:           dt.datetime
        direction:      'long'/'short'
        symbol:         string
        open:           'open'/'close'
        orderType:      'MARKET'/'LIMIT'
        number:         int
        limit_price:    float
        '''

        self.tradeID = tradeID
        self.orderID = orderID
        self.time =  time
        self.direction = direction
        self.open = open
        self.symbol = symbol
        self.orderType = orderType
        self.number = number
        self.limitPrice = limitPrice

class simClock(object):

    def __init__(self):

        self.timeIndex = None
        self.now = None

    def initializeTimeIndex(self,timeIndex):
        self.timeIndex = timeIndex

    def mark(self,timestamp):
        if timestamp not in self.timeIndex:
            self.timeIndex = self.timeIndex.insert(
                self.timeIndex.searchsorted(timestamp), timestamp)

    def updateTime(self):
        self.now = self.timeIndex[0]
        self.timeIndex = self.timeIndex.delete(0)

class cycleManager(object):

    def __init__(self):

        self.cycleBeginDate = None
        self.cycleEndDate = None
        self.cycleBeginTimeDelta = None
        self.cycleEndTimeDelta = None

        #if the each cycle go through time 00:00:00
        self.crossMidNight = False

        #cycles: store the begin and end datetime of each cycle
        #cycles = [cycle1,cycle2,...]
        self.cycles = []


    def initializeCycle(self, begindate, begintime, enddate, endtime):
            '''
            parse the begin datetime and end datetime
            generate self.cycle based on input
            '''

            begintime = strptime(begintime, '%H:%M:%S')
            endtime = strptime(endtime, '%H:%M:%S')

            OneDayDelta = dt.timedelta(0)


            if endtime > begintime:
                self.crossMidNight = False
            elif endtime < begintime:
                self.crossMidNight = True
                OneDayDelta = dt.timedelta(1)
            else:
                #begintime = endtime not allowed
                print 'begintime cannot be the same as endtime'

            self.cycleBeginTimeDelta = dt.timedelta(hours= begintime.tm_hour,minutes = begintime.tm_min, seconds = begintime.tm_sec)
            self.cycleEndTimeDelta = dt.timedelta(hours= endtime.tm_hour,minutes = endtime.tm_min, seconds = endtime.tm_sec)
            self.cycleBeginDate = parse(begindate)
            self.cycleEndDate = parse(enddate)

            beginDateRange = list(rrule.rrule(rrule.DAILY, dtstart = self.cycleBeginDate, until = self.cycleEndDate))

            for beginDate in beginDateRange:
                element = {'beginDate':beginDate,
                        'endDate':beginDate + OneDayDelta,
                        'beginTime':beginDate + self.cycleBeginTimeDelta,
                        'endTime':beginDate + OneDayDelta + self.cycleEndTimeDelta}
                self.cycles.append(element)

class simulator(object):

    def __init__(self):

        #the simulated clock
        self.simClock = simClock()

        self.dataEngine = dataEngine

        #used to load data from kdb
        self.dataloader = simDataLoader()

        self.dataCells = []

        self.cycleManager = cycleManager()

        #store the match between trader symbol and market data index
        #key:symbol value:int - index of market data
        self.symbol_market_pair = defaultdict()

        #self.traderLoader = va.strategy.trader.TraderLoader()
        self.trader = None
        self.traderparams = None

        self.dailyStopDelta = 0

        self.initialcapital = 1000000.0

        #store symbol traded in the portfolio
        self.portfolioSymbol = set()

        self.portfolio = pd.DataFrame(
            dict(time=dt.datetime(1990,1,1),symbol='VSCHON',price=np.zeros(100000),
                 number=np.zeros(100000),direction='long',
                 open = 'open', tradeID = np.zeros(100000),
                 cash=np.zeros(100000),value=np.zeros(100000)),
            columns = ['time', 'tradeID', 'symbol','price','number','direction','open','cash','value'])
        self.tradeIndex = 0
        self.tradeVerbose = True

    def setData(self, datalist):
        self.trader.setTradedSymbol(datalist)
        self.dataEngine.setData(datalist)


    def initializeCycle(self, begindate, begintime, enddate, endtime):
        self.cycleManager.initializeCycle(begindate, begintime, enddate, endtime)

    def setDailyStopDelta(self,deltaSeconds):
        '''
        set the time trader do not enter new positions
        '''

        self.dailyStopDelta = dt.timedelta(0,deltaSeconds)

    def setcapital(self,value):
        '''
        set the initial value of simulation value
        defaul to be 1 million
        '''
        self.initialcapital = value

    def setTradeVerbose(self, tradeVerbose):
        self.tradeVerbose = tradeVerbose


    def linkTrader(self,trader):
        '''
        set the trader for simulation
        '''
        self.trader = trader
        self.trader.linkSimulator(self)

    def setTraderParams(self,params):
        self.traderparams = params


    def replaceData(self,cycle):

        '''
        replace 1 cycle data into simulator for dispatch
        '''

        timeIndex = self.dataEngine.replaceData(cycle)

        self.simClock.initializeTimeIndex(timeIndex)

    def __printTrade(self,trade):
        print trade['time'].strftime(format = "%Y%m%d %H:%M:%S.%f") + " ",
        print "%s %s %d %s at %f" % (trade['open'], trade['direction'], trade['number'], trade['symbol'], trade['price'])

    def updatePortfolio(self,trade):
        '''
        update portfolio based on new trades
        '''
        #ipdb.set_trace()

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
            tempprice =  self.matcherlist[sym].singleprice(time,sym,self.market[sym])
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


    def orderProcessor(self, order):

        '''
        callback function to receive order from trader
        '''
        trade =  self.dataEngine.fillOrder(order)

        if trade != 'NA':
            self.updatePortfolio(trade)


    def simulate(self):

        '''
        for each day from begindate to enddate,
        load the data and dispatch it to registered strategies
        if the data loaded include timestamps outside of the tima range,
        to be modified
        '''

        #self.statuscheck()
        #if self.ready == False:
        #    return -1

        for cycle in self.cycleManager.cycles:
            '''
            simulate for each cycle in cycles
            '''

            #ipdb.set_trace()
            #load new data into simulator
            self.replaceData(cycle)

            #set daily stop time
            stoptime = cycle['endTime'] - self.dailyStopDelta
            self.trader.setStopTime(stoptime)

            #reset trader parameters
            self.trader.setparams(self.traderparams)

            #execute algo
            if len(self.simClock.timeIndex) > 0:
                self.trader.run()

        self.portfolio = self.portfolio[self.portfolio['price']!=0]
        self.__portfolioAnalyzer()

        print 'Simulation completed'

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
        cycles = self.cycleManager.cycles
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


