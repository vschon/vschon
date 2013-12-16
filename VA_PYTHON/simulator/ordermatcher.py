import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
from VA_PYTHON.datamanage.datahandler import Sender
from collections import defaultdict
import datetime as dt
from time import strptime
from dateutil import rrule
from dateutil.parser import parse
import types
import ipdb


class forex_quote_matcher():
    '''
    used to match transactions in forex_quote database
    '''

    def __init__(self):

        #delay in milliseconds
        self.delay = dt.timedelta(0,0,0)

    def setdelay(self,delay):
        '''
        set transaction delay (in milliseconds)
        '''
        self.delay = dt.timedelta(0,0,delay)

    def fetchpoint(self,time,symbol,hdb):
        '''
        get point from hdb
        '''
        symbolhdb = hdb[hdb['symbol']==symbol.upper()]
        state = symbolhdb[:time].ix[-1]
        return state

    def singleprice(self,time,symbol,hdb):

        symbolhdb = hdb[hdb['symbol']==symbol.upper()]
        state = symbolhdb[:time].ix[-1]
        price = 0.5*(state['ask'] + state['bid'])
        return price


    def marketmatch(self,order,hdb):
        #ipdb.set_trace()
        transactTime = order['time'] + self.delay

        #extract the data of the symbol
        state = self.fetchpoint(transactTime,order['symbol'],hdb)

        if order['direction'] == 'long':
            transactPrice = state['ask']
        elif order['direction'] == 'short':
            transactPrice = state['bid']

        trade = {'time':transactTime,
                 'price':transactPrice,
                 'direction':order['direction'],
                 'symbol':order['symbol'],
                 'number':order['number'],
                 'open':order['open']}

        return trade

    def match(self,order,hdb):
        trade = None
        if order['type'] == 'MARKET':
            trade = self.marketmatch(order,hdb)
        elif order['type'] == 'LIMIT':
            pass
        return trade
