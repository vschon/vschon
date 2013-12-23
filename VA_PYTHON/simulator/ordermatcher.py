import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_DATABASE as vd
#from VA_PYTHON.datamanage.datahandler import Sender
from collections import defaultdict
import datetime as dt
from time import strptime
from dateutil import rrule
from dateutil.parser import parse
import types
import ipdb

class orderMatcher(object):

    def __init__(self):
        #delay in milliseconds
        self.delay = dt.timedelta(0, 0, 2000)

    def setdelay(self,microsecondDelay):
        '''
        set transaction delay (in microseconds)
        '''
        self.delay = dt.timedelta(0,0,microsecondDelay)

    def fetchpoint(self,time,symbol,hdb):
        '''
        get point from hdb
        '''
        symbolhdb = hdb[hdb['symbol']==symbol.upper()]
        state = symbolhdb[:time].ix[-1]
        return state

    def match(self,order,hdb):
        trade = None
        if order.orderType == 'MARKET':
            trade = self.matchMarketOrder(order,hdb)
        elif order.orderType == 'LIMIT':
            pass
        return trade

    def matchMarketOrder(self):
        pass

    def singlePrice(self):
        pass

class forex_quoteMatcher(orderMatcher):
    '''
    used to match transactions in forex_quote database
    '''

    def singlePrice(self,time,symbol,hdb):

        symbolhdb = hdb[hdb['symbol']==symbol.upper()]
        state = symbolhdb[:time].ix[-1]
        price = 0.5*(state['ask'] + state['bid'])
        return price


    def matchMarketOrder(self,order,hdb):
        #ipdb.set_trace()
        transactTime = order.time + self.delay

        #extract the data of the symbol
        state = self.fetchpoint(transactTime,order.symbol,hdb)

        if order.direction == 'long':
            transactPrice = state['ask']
        elif order.direction == 'short':
            transactPrice = state['bid']

        trade = {'time':transactTime,
                 'price':transactPrice,
                 'direction':order.direction,
                 'symbol':order.symbol,
                 'number':order.number,
                 'open':order.open,
                 'tradeID': order.tradeID}
        return trade


