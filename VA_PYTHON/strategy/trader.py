import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
from collections import defaultdict
import datetime as dt
from dateutil.parser import parse

import ipdb

class trader(object):
    '''
    virtual class for trader
    It should be overriden by real trader functions
    '''

    def __init__(self):

        self.name = ''
        self.currentStat = None
        self.stateUpdate = False

        self.symbols = []
        self.filter = []
        self.timer = None
        self.now = None
        self.sender = []

        self.simIncrementTime = None

        self.END = 5000*10000

        #trader will not enter into new positions after DailyStopTime
        self.DailyStopTime = None

        self.reverse = False
        self.dir_long = 'long'
        self.dir_short = 'short'

    def setname(self,name):
        self.name = name

    def setsymbols(self,symbols):
        '''
        set symbols to be sent out by trader
        '''

        self.symbols = va.utils.utils.formlist(symbols)

    def setsimtimer(self,initialtime,increment):
        '''
        time used to update time for simulatiorn mode
        beginTime:str,the beginning time of simulation timer
        increment:int, the smallest increment(in micro-seconds) of the timer
        '''

        self.timer = self.simtimer
        self.now = initialtime
        self.simIncrementTime = dt.timedelta(0,0,increment)

    def simtimer(self):
        '''
        simulation timer
        '''
        self.now = self.now + self.simIncrementTime

    def realtimer(self):
        '''
        real timer
        '''

        self.now = dt.datetime.now()


    def setsender(self,senders):
        '''
        senders:[func1,func2]
        func1,2 are the callback function of brokers
        senders pass the api for each sender
        set sender for each symbol in the trader.symbols
        '''

        senders = va.utils.utils.formlist(senders)

        for sender in senders:
            temp = None
            temp = OrderSender(self,sender)
            self.sender.append(temp)

    def setfilter(self,filters):
        '''
        set the filter for each arm of trader
        filter name is the name of the table in DB
        '''

        filters = va.utils.utils.formlist(filters)
        for filter in filters:
            filter_name,fetch_name = filter.split('-')
            temp = None
            if filter_name == 'forex_quote':
                temp = va.strategy.filter.forex_quoteFilter()
                temp.setFetcher(fetch_name)
            else:
                pass
            self.filter.append(temp)

        for item in self.filter:
            item.linkTrader(self)

    def linkimdb(self,imdblist):
        '''
        pass imdb to the trader filter
        input:[imdb0,imdb1]
        imdb0,1 matches self.filter[0] self.filter[1]

        reset to counter to zeros imdb is updated
        '''

        imdblist = va.utils.utils.formlist(imdblist)
        for i in range(len(imdblist)):
            self.filter[i].setDataSource(imdblist[i])
            self.filter[i].resetCounter()

    def setStopTime(self,DailyStopTime):
        '''
        set daily stop time
        trader will not open new positions after stop time
        '''
        self.DailyStopTime = DailyStopTime


    def setparams(self,params):
        '''
        set the parameters of trader
        '''
        pass

    def Reverse(self,reverse):
        '''
        if reverse = true, trader will sent reverse the direction of trading.
        '''
        self.reverse = reverse
        if reverse == True:
            self.dir_long = 'short'
            self.dir_short = 'long'


    ####CORE-BEGIN####
    def updatestate(self):
        '''
        update state value at current time
        '''
        pass

    def logic(self):
        '''
        make trading decisions based on current state
        '''
        pass

    def run(self):
        '''
        working flow of updatestate() and logic()
        '''
        for i in range(self.END):
            #print i
            self.timer()

            self.updatestate()

            self.logic()

    ####CORE-END####

class OrderSender(object):

    def __init__(self,trader,apireceiver):
        self.trader = trader
        self.apireceiver = apireceiver
        self.SendOrder = None
        self.orderID = 0


        if isinstance(self.trader,va.strategy.hawkes.hawkes.hawkesTrader):
            #for hawkes trader
            if apireceiver.__name__ == 'simOrderProcessor':
                self.SendOrder = self.SendOrder_hawkes2sim


    def SendOrder_hawkes2sim(self,direction,open,symbol,number):
        '''
        SendOrder from  hawkes trader to simulator
        '''

        time = self.trader.now
        order = va.simulator.simulator.generateSimOrder(id = self.orderID,
                                                        time = time,
                                                        symbol = symbol,
                                                        direction = direction,
                                                        open = open,
                                                        orderType = 'MARKET',
                                                        number = number)
        self.orderID += 1
        self.apireceiver(order)


class TraderLoader():
    '''
    Save and Initialzie all traders
    return a trader object when called
    '''
    def __init__(self):
        '''
        Initializng traders
        '''
        self.traderlib = {}
        self.traderlib['hawkes'] = va.strategy.hawkes.hawkes.hawkesTrader()

    def load(self,trader):
        if trader in self.traderlib.keys():
            return self.traderlib[trader]
        else:
            print 'trader name not in trader library'
            return -1
