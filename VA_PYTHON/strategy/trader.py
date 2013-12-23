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

        self.simulator = None

        self.name = 'Anonymous Trader'
        self.currentStat = None
        self.stateUpdate = False

        self.symbols = []

        #trader will not enter into new positions after DailyStopTime
        self.DailyStopTime = None

        self.reverse = False
        self.dir_long = 'long'
        self.dir_short = 'short'
        self.now = None

        self.orderID = 1
        self.tradeID = 1

    def linkSimulator(self,simulator):
        self.simulator = simulator

    def setname(self,name):
        self.name = name

    def setTradedSymbols(self,symbols):
        '''
        set symbols to be sent out by trader
        '''

        self.symbols = va.utils.utils.formlist(symbols)

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
            self.simulator.orderProcessor(order)

            return tradeID



    ####CORE-BEGIN####
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
        while len(self.simulator.simClock.timeIndex) > 0:
            #print i
            self.simulator.simClock.updateTime()
            self.now = self.simulator.simClock.now

            self.updateState()

            self.logic()

    ####CORE-END####

