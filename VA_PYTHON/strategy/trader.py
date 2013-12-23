import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_DATABASE as vd
from collections import defaultdict
import datetime as dt
from dateutil.parser import parse
from VA_PYTHON.simulator.simulator import simOrder
import ipdb

class trader(object):
    '''
    virtual class for trader
    It should be overriden by real trader functions
    '''

    def __init__(self):

        self.simClock = va.simulator.simulator.simClock()
        self.dataEngine = va.simulator.dataengine.dataEngine()
        self.cycleManager = va.simulator.simulator.cycleManager()
        self.portfolioManager = va.simulator.portfolioManager.portfolioManager(self)

        self.name = 'Anonymous Trader'

        self.currentStat = None
        self.stateUpdate = False

        self.symbols = []
        self.number = 100

        #trader will not enter into new positions after DailyStopTime
        self.DailyStopTime = None
        self.dailyStopDelta = 0

        self.reverse = False
        self.dir_long = 'long'
        self.dir_short = 'short'
        self.now = None

        self.orderID = 1
        self.tradeID = 1

    def simulate(self):

        '''
        for each day from begindate to enddate,
        load the data and dispatch it to registered strategies
        if the data loaded include timestamps outside of the tima range,
        to be modified
        '''

        for cycle in self.cycleManager.cycles:
            '''
            simulate for each cycle in cycles
            '''

            #load new data into simulator
            self.replaceData(cycle)

            #set daily stop time
            stoptime = cycle['endTime'] - self.dailyStopDelta
            self.setStopTime(stoptime)

            #reset trader parameters
            self.updateTrader()

            #execute algo
            if len(self.simClock.timeIndex) > 0:
                self.run()
                self.portfolioManager.recordEndCyclePortfolio(cycle['endTime'])

        print 'Simulation completed'
        self.portfolioManager.summarize()

    def setname(self,name):
        self.name = name

    def setStopTime(self,DailyStopTime):
        '''
        set daily stop time
        trader will not open new positions after stop time
        '''
        self.DailyStopTime = DailyStopTime


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

    def setData(self, datalist):
        self.dataEngine.setData(datalist)
        self.symbols = va.utils.utils.formlist(datalist)

    def initializeCycle(self, begindate, begintime, enddate, endtime):
        self.cycleManager.initializeCycle(begindate, begintime, enddate, endtime)

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

    def Reverse(self,reverse):
        '''
        if reverse = true, trader will sent reverse the direction of trading.
        '''
        self.reverse = reverse
        if reverse == True:
            self.dir_long = 'short'
            self.dir_short = 'long'

    def trade(self, direction, open, symbol, number, orderType = 'MARKET', tradeID = 0):

            if open == 'open':
                tradeID = self.tradeID
                self.tradeID += 1
            orderID = self.orderID
            orderID += 1
            #ipdb.set_trace()

            order = simOrder(
                    orderID = orderID,
                    tradeID = tradeID,
                    time = self.now,
                    symbol = symbol,
                    direction = direction,
                    open = open,
                    orderType = orderType,
                    number = number)
            self.orderProcessor(order)

            return tradeID

    ####CORE-BEGIN####

    def initialize(self):
        pass

    def updateTrader(self):
        '''
        set the parameters of trader
        '''
        pass

    def updateState(self):
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
        working flow of updateState() and logic()
        '''
        while len(self.simClock.timeIndex) > 0:

            self.simClock.updateTime()
            self.now = self.simClock.now

            self.updateState()

            self.logic()

    ####CORE-END####

