import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
import datetime as dt
from collections import defaultdict

import ipdb

class SimFilter(object):
    '''
    virtual class to fetch date from database
    all sim filter should inheritate from class Sim Filter
    '''

    def __init__(self):
        self.datasource = []
        self.counter = 0
        self.fetch = None
        self.trader = None

    def linkTrader(self,trader):
        '''
        pass trader object to filter so filter can get trader time
        '''

        self.trader = trader


    def setFetcher(self,fetch):
        '''
        set fetch function of filter
        '''
        if fetch == 'single_price':
            self.fetch = self.fetch_singlePrice
        elif fetch == 'double_price':
            self.fetch = self.fetch_doublePrice
        elif fetch == 'fetch':
            if self.fetch == None:
                print 'Warning, fetch() in the fileter is None'

    def setDataSource(self,datasource):
        '''
        set the data source to be fetched
        '''
        self.datasource = datasource

    def resetCounter(self):
        '''
        reset counter to zero
        '''
        self.counter = 0

    def fetch_singlePrice():
        '''
        fetch single price data from database

        return {'time':XX,'price':XX,...}
        '''
        pass

    def fetch_doublePrice():
        '''
        fetch ask/bid price data from database

        return {'time':XX,'ask':XX,'bid':XX,...}
        '''
        pass


class forex_quoteFilter(SimFilter):
    '''
    filter for forex_quote DB
    linking to the in memory database
    all sim filter should inheritate from class Sim Filter
    '''

    def fetch_singlePrice(self):
        '''
        fetch data from database

        incoming data structure:

        tuple
        0:time/
        1:date/
        2:symbol/
        3:time/
        4:bid/
        5:ask

        return:{'time':XX, 'price':XX}
        '''

        #for simulation, if trader's time is earlier
        #than the next point arrival time, then do not return next point
        if self.counter < len(self.datasource):
            #there are remaining data to be fetched
            point = self.datasource[self.counter]
            if self.trader.now >= point[3]:
                self.counter += 1
                return {'time':point[0].to_datetime(),'price':(point[4]+point[5])/2.0}
            else:
                return -1
        else:
            return -1


