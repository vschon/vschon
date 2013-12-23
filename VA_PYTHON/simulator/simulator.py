import numpy as np
import pandas as pd
import math
import VA_PYTHON as va
from VA_PYTHON.simulator.dataengine import *
from VA_PYTHON.simulator.portfolioManager import *
import VD_DATABASE as vd
from collections import defaultdict
import datetime as dt
from time import strptime
from dateutil import rrule
from dateutil.parser import parse
import types
import ipdb

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

        self.dataEngine = dataEngine()

        self.cycleManager = cycleManager()

        #self.traderLoader = va.strategy.trader.TraderLoader()
        self.trader = None
        self.traderparams = None

        self.dailyStopDelta = 0

        self.portfolioManager = portfolioManager(self)

    def setData(self, datalist):
        self.trader.setTradedSymbols(datalist)
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
        self.portfolioManager.setcapital(value)

    def setTradeVerbose(self, tradeVerbose):
        self.portfolioManager.setTradeVerbose = tradeVerbose


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


    def orderProcessor(self, order):

        '''
        callback function to receive order from trader
        '''
        trade =  self.dataEngine.fillOrder(order)

        if trade != 'NA':
            self.portfolioManager.updatePortfolio(trade)


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

        print 'Simulation completed'
        self.portfolioManager.summarize()


