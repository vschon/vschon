import numpy as np
import pandas as pd
import math
import VA_PYTHON as va
import VD_KDB as vd
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

class simDataLoader():

    def __init__(self):
        self.conn = vd.pyapi.kdblogin()

    def load(self,command):
        '''
        the base function
        load data from kdb into pd time series
        '''

        result = vd.pyapi.qtable2df(self.conn.k(command))
        if 'time' in result.columns:
            result.index = result['time']

        return result

    def tickerload(self,source,symbol,begindate,enddate = None):
        '''
        load data as df
        '''

        if enddate == None:
            enddate = begindate

        daterange = '(' + begindate + ';' + enddate + ')'

        if source != symbol:
            command = 'select from ' + source + ' where date within ' + \
                    daterange + ',symbol=`' + symbol.upper()
        else:
            command = 'select from ' + source + ' where date within ' +  daterange

        return self.load(command)


def generateSimOrder(id,time,direction,open,
                     symbol,orderType,number,
                     limit_price=0):
    '''
    id:             order ID
    time:           dt.datetime
    direction:      'long'/'short'
    symbol:         string
    open:           True/False
    orderType:      'MARKET'/'LIMIT'
    number:         int
    limit_price:    float
    '''
    return {'orderID':      id,
            'time':         time,
            'direction':    direction,
            'open':         open,
            'symbol':       symbol,
            'type':         orderType,
            'number':       number,
            'limit_price':  limit_price}


class simulator():

    def __init__(self):

        #used to load data from kdb
        self.dataloader = simDataLoader()

        #hdb: holds data from different datasource in df type
        self.hdb = []

        #IMDB is the in memory database to be sent to trader
        self.IMDB = []

        #market: hold data in pd dataframe type, used for transaction matching
        self.market = []

        #Store HDB data list
        #market data first, non-markte data last
        self.datalist = []

        #Store market data list
        self.marketlist = []

        #store the match between trader symbol and market data index
        #key:symbol value:int - index of market data
        self.symbol_market_pair = defaultdict()

        #store the order matcher for each market data
        self.matcher = []

        #testing cycle config
        self.cycleBeginDate = None
        self.cycleEndDate = None
        self.cycleBeginTimeDelta = None
        self.cycleEndTimeDelta = None

        #if the each cycle go through time 00:00:00
        self.crossMidNight = False

        #cycles: store the begin and end datetime of each cycle
        #cycles = [cycle1,cycle2,...]
        self.cycles = []


        self.traderLoader = va.strategy.trader.TraderLoader()
        self.trader = None
        self.traderparams = None

        self.dailyStopDelta = 0

        self.initialcapital = 1000000.0

        #store symbol traded in the portfolio
        self.portfolioSymbol = set()

        self.portfolio = pd.DataFrame(
            dict(time=dt.datetime(1990,1,1),symbol='VSCHON',price=np.zeros(100000),
                 number=np.zeros(100000),direction='long',
                 open = True,
                 cash=np.zeros(100000),value=np.zeros(100000)),
            columns = ['time','symbol','price','number','direction','open','cash','value'])
        self.tradeIndex = 0


    def setdatalist(self, datalist):
        '''
        fill datalist in a convenient way

        input:
            datalist: tuple of ('forex_quote-usdjpy','source-symbol')
            market data first, non-market data last

        output:
            list of dict
            self.datalist:[{'name':symbol,'source':source},...]
        '''

        if type(datalist) is not types.TupleType and type(datalist) is not list:
            datalist = (datalist, )

        for SourceSymbol in datalist:
            try:
                [source, symbol] = SourceSymbol.split('-')
                temp = {}
                temp['name'] = symbol
                temp['source'] = source
                self.datalist.append(temp)
            except ValueError:
                source = SourceSymbol
                temp = {}
                temp['name'] = source
                temp['source'] = source
                self.datalist.append(temp)

    def emptydatalist(self):
        self.datalist = []

    def setMarketList(self,n):
        '''
        choose the data used for transaction matching
        set the order matched based on market data source
        set the delay time of each order mathcer (unit:millisecond)

        input: the first n element in datalist as market list
        '''

        self.marketlist = self.datalist[:n]

    def setOrderMatcher(self,matcherlist):

        if type(matcherlist) is not types.TupleType and type(matcherlist) is not list:
            matcherlist = [matcherlist,]

        #set the corresponding order matcher
        for element in matcherlist:
            if element == 'forex_quote':
                temp = va.simulator.ordermatcher.forex_quote_matcher()
            else:
                print 'no ' + element + '!'
            self.matcher.append(temp)

    def setDelayTime(self,delayList):
        '''
        set the delay time for each mather

        input:
            [3,2]
            delay microseconds for each matcher
        '''

        if type(delayList) is not types.TupleType and type(delayList) is not list:
            delayList = (delayList,)

        for i in range(len(delayList)):
            self.matcher[i].setdelay(delayList[i])


    def matchSymbol(self,pairs):
        '''
        match the symbol sent from trader and the symbol in the market data

        input:
            symbol: list of symbol pair
                    ['ABC-0','DEF-1']
                    'ABC':symbol sent from trader
                    0: index of symbol in the self.market
        '''

        if type(pairs) is not types.TupleType and type(pairs) is not list:
            pairs = (pairs,)
        for pair in pairs:
            [symbol,index] = pair.split('-')
            self.symbol_market_pair[symbol] = int(index)

    def linksender(self):
        for element in self.trader.sender:
            element.linkTrader(self.trader)
            element.linkSimulator(self)


    def setCycle(self, begindate, begintime, enddate, endtime):
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

        #Initializing

    def setDailyStopDelta(self,delta):
        '''
        set the time trader do not enter new positions
        '''

        self.dailyStopDelta = dt.timedelta(0,delta)

    def setSimTimerIncrement(self,increment):
        '''
        set the increment of sim timer of trader
        '''
        self.simTimerIncrement = increment

    def setcapital(self,value):
        '''
        set the initial value of simulation value
        defaul to be 1 million
        '''
        self.initialcapital = value


    def setTrader(self,trader):
        '''
        set the trader for simulation
        '''
        if trader in self.traderLoader.traderlib.keys():
            self.trader = self.traderLoader.load(trader)
        else:
            print 'trader name not in trader library!'

    def setTraderParams(self,params):
        self.traderparams = params


    def replaceData(self,cycle):

        '''
        replace 1 cycle data into simulator for dispatch
        '''
        #ipdb.set_trace()

        self.hdb = []
        self.market = []
        self.IMDB = []

        for element in self.datalist:
            beginDate = cycle['beginDate'].strftime('%Y.%m.%d')
            endDate = cycle['endDate'].strftime('%Y.%m.%d')

            temp = self.dataloader.tickerload(symbol= element['name'], source = element['source'],begindate = beginDate, enddate = endDate)
            temp = temp.drop_duplicates(cols = 'time')
            temp = temp[cycle['beginTime'].strftime('%Y-%m-%d %H:%M:%S'):cycle['endTime'].strftime('%Y-%m-%d %H:%M:%S')]

            #updating hdb and imdb
            self.hdb.append(temp)
            self.IMDB.append(list(temp.itertuples()))

        #updating market data
        for j in range(len(self.marketlist)):
            self.market.append(self.hdb[j])


    def updatePortfolio(self,trade):
        '''
        update portfolio based on new trades
        '''
        #ipdb.set_trace()

        if self.tradeIndex%100000 == 0 and self.tradeIndex!=0:
            portfolio_copy = self.portfolio[:100000].copy()
            portfolio_copy['price'] = dt.datetime(1990,1,1)
            portfolio_copy['symbol'] = 'VSCHON'
            portfolio_copy['price'] = 0.0
            portfolio_copy['number'] = 0.0
            portfolio_copy['direction'] = 'long'
            portfolio_copy['open'] = True
            portfolio_copy['cash'] = 0.0
            portfolio_copy['value'] = 0.0
            self.portfolio = pd.concat([self.portfolio,portfolio_copy],ignore_index=True)

        time = trade['time']
        symbol = trade['symbol']
        price = trade['price']
        direction = trade['direction']
        number = trade['number']
        open = trade['open']

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

        if self.tradeIndex == 0:
            #special case for first trade
            #update cash
            self.portfolio['cash'][self.tradeIndex] = self.initialcapital - mark*number*price

            #update traded symbol number
            if open == True:
                if direction == 'long':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = number
                elif direction == 'short':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = number
            elif open == False:
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
            if open == True:
                if direction == 'long':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = number + self.portfolio.ix[self.tradeIndex][symbol + '-long']
                elif direction == 'short':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = number + self.portfolio.ix[self.tradeIndex][symbol + '-short']
            elif open == False:
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

        print trade
        print self.portfolio['value'][self.tradeIndex]
        self.tradeIndex += 1


    def simOrderProcessor(self, order):

        '''
        callback function to receive order from trader
        '''
        #ipdb.set_trace()

        #translate order symbol into market symbol
        index = self.symbol_market_pair[order['symbol']]

        #match trade
        trade =  self.matcher[index].match(order,self.market[index])

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

        for cycle in self.cycles:
            '''
            simulate for each cycle in cycles
            '''

            #load new data into simulator
            self.replaceData(cycle)

            #pass imdb to filters of trader
            self.trader.linkimdb(self.IMDB)
            #self.trader.linkimdb([self.IMDB[0],self.IMDB[1]])

            #set new cycle begin time of trader
            begintime = cycle['beginTime'] - dt.timedelta(0,180)
            self.trader.setsimtimer(begintime,self.simTimerIncrement)

            #set daily stop time
            stoptime = cycle['endTime'] - self.dailyStopDelta
            self.trader.setStopTime(stoptime)

            #reset trader parameters
            self.trader.setparams(self.traderparams)

            #execute algo
            self.trader.run()

        print 'Simulation completed'

    def portfolioAnalyzer(self,portfolio,cycles,initialValue):
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

        result = portfolio[portfolio['price'] != 0]
        result.index = result['time']
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


