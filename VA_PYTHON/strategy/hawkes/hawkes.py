import numpy as np
import pandas as pd
import VD_DATABASE as vd
from VA_PYTHON.strategy.trader import trader
from VA_PYTHON.simulator.simulator import simOrder
import datetime as dt
from collections import defaultdict
import math
import types
from dateutil.parser import parse

import ipdb


class hawkesTrader(trader):

    '''
    object to implement hawkes trading strategy
    '''

    def __init__(self):

        trader.__init__(self)

        #initialize the state
        self.currentState = {'time':None,
                      'price':0,
                      'pos':None,
                      'neg':None,
                      'rate':None}
        self.stateUpdated = False

        #parameters
        self.a11 = 0.1
        self.a12 = 0.6
        self.a21 = 0.6
        self.a22 = 0.1
        self.mu1 = 0.5
        self.mu2 = 0.5
        self.beta1 = 1.0
        self.beta2 = 1.0
        self.threshold = 3.0
        self.exitdelta = dt.timedelta(0,5)
        self.number = 0

        #store the pending exit
        self.PendingExit = []


    def setparams(self,params):
        '''
        settthe parameters of hawkes process
        otherwise, use default
        re_initialze current state
        '''

        #set theta
        theta = params['theta']

        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:8]).reshape(2,1)

        #set the number of units to trade
        self.number = params['number']

        #set the threshold for trigerring trades
        self.threshold = params['k']

        #set time in seconds to exit an opened positions(in seconds)
        self.exitdelta = dt.timedelta(0, params['exitdelta'])

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

        #ipdb.set_trace()

        value = self.simulator.dataCells[0].getPoint(self.now)
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
                    self.simulator.simClock.mark(exitTime)

                elif self.currentState['rate'] < 1/self.threshold:
                    entryTradeID = self.trade(direction = self.dir_short, open = 'open', symbol = self.symbols[0],
                               number = self.number, orderType = 'MARKET')
                    exitTime = self.now + self.exitdelta
                    self.PendingExit.append({'time': exitTime, 'direction':self.dir_long, 'tradeID': entryTradeID})
                    self.simulator.simClock.mark(exitTime)
                self.stateUpdated = False


