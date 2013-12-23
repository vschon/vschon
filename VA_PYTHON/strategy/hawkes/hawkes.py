import numpy as np
import pandas as pd
from VA_PYTHON.strategy.trader import trader
import datetime as dt
import math

import ipdb


class hawkesTrader(trader):

    '''
    object to implement hawkes trading strategy
    '''

    def initialize(self,params = None):
        #initialize the state
        self.currentState = {'time':None,
                      'price':0,
                      'pos':None,
                      'neg':None,
                      'rate':None}
        self.stateUpdated = False

        #store the pending exit
        self.PendingExit = []

        #parameters
        if params == None:
            self.mu1, self.mu2, self.a11, self.a12, self.a21, self.a22, self.beta1, self.beta2 = 0.5, 0.5, 0.1, 0.6, 0.6, 0.1, 1.0, 1.0
            self.threshold = 3.0
            self.exitdelta = dt.timedelta(seconds = 5)
            self.number = 100
            self.dailyStopDelta = dt.timedelta(seconds = 300)
        else:
            self.mu1, self.mu2, self.a11, self.a12, self.a21, self.a22, self.beta1, self.beta2 = params['theta']
            self.threshold = params['k']
            self.exitdelta = dt.timedelta(seconds = params['exitPositionDeltaSeconds'])
            self.number = params['number']
            self.dailyStopDelta = dt.timedelta(seconds = params['stopTradingDeltaSeconds'])


    def updateTrader(self):
        '''
        re_initialze current state
        '''

        #reinitialize state
        self.currentState['price'] = 0.0
        self.currentState['pos'] = self.mu1
        self.currentState['neg'] = self.mu2
        self.currentState['rate'] = self.mu1/self.mu2

    def updateState(self):
        '''
        get data from imdb
        update state
        '''

        value = self.dataEngine.getPoint(self.symbols[0], self.now)

        if value['state'] == 'SUCCESS':
            point = value['data']
            price = (point['bid'] + point['ask']) / 2.0
            time = point['time']

            if self.currentState['price'] == 0:
                self.currentState['price'] = price
                self.currentState['time'] = time
            elif price != self.currentState['price']:
                delta = (time - self.currentState['time']).total_seconds()
                mark = price - self.currentState['price']

                if mark > 0:
                    self.currentState['pos'] = (self.currentState['pos'] - self.mu1)/math.exp(self.beta1*delta) + self.mu1 + self.a11
                    self.currentState['neg'] = (self.currentState['neg'] - self.mu2)/math.exp(self.beta2*delta) + self.mu2 + self.a21
                else:
                    self.currentState['pos'] = (self.currentState['pos'] - self.mu1)/math.exp(self.beta1*delta) + self.mu1 + self.a12
                    self.currentState['neg'] = (self.currentState['neg'] - self.mu2)/math.exp(self.beta2*delta) + self.mu2 + self.a22

                self.currentState['rate'] = self.currentState['pos']/self.currentState['neg']
                self.currentState['time'] = time
                self.currentState['price'] = price

                self.stateUpdated = True

    def logic(self):

        #Exit existing positions
        if len(self.PendingExit) > 0:
            #if there is pending exit positions

            while self.now >= self.PendingExit[0]['time']:
                #Order(self.PendingExit)
                temp_order = self.PendingExit[0]
                self.trade(tradeID = temp_order['tradeID'], direction=temp_order['direction'],open='close',symbol=self.symbols[0],number=self.number)
                self.PendingExit.pop(0)
                if len(self.PendingExit) == 0:
                    break

        #Enter new positions
        if self.now < self.DailyStopTime:
            if self.stateUpdated == True:
                #print self.currentState
                if self.currentState['rate'] > self.threshold:
                    entryTradeID = self.trade(direction = self.dir_long, open = 'open', symbol = self.symbols[0],
                               number = self.number, orderType = 'MARKET')
                    exitTime = self.now + self.exitdelta
                    self.PendingExit.append({'time': exitTime, 'direction': self.dir_short, 'tradeID': entryTradeID})
                    self.simClock.mark(exitTime)

                elif self.currentState['rate'] < 1/self.threshold:
                    entryTradeID = self.trade(direction = self.dir_short, open = 'open', symbol = self.symbols[0],
                               number = self.number, orderType = 'MARKET')
                    exitTime = self.now + self.exitdelta
                    self.PendingExit.append({'time': exitTime, 'direction':self.dir_long, 'tradeID': entryTradeID})
                    self.simClock.mark(exitTime)
                self.stateUpdated = False


