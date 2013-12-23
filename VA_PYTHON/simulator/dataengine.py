import numpy as np
import pandas as pd
import math
import VA_PYTHON as va
import VD_DATABASE as vd
from collections import defaultdict
import datetime as dt
from time import strptime
from dateutil import rrule
from dateutil.parser import parse
import types
import ipdb

forex_quote_source = set('AUDJPY','AUDNZD','AUDUSD','CADJPY',
                         'CHFJPY','EURCHF','EURGBP','EURJPY',
                         'EURUSD','GBPJPY','GBPUSD','NZDUSD',
                         'USDCAD','USDCHF','USDJPY')
class simDataLoader():

    def __init__(self):
        self.conn = vd.kdbAPI.kdblogin()

    def load(self,command):
        '''
        the base function
        load data from kdb into pd time series
        '''

        result = vd.kdbAPI.qtable2df(self.conn.k(command))
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


class dataCell(object):

    def __init__(self, symbol, source):
        self.source = source
        self.symbol = symbol
        self.data = None
        self.orderMatcher = None
        self.__setOrderMatcher()

    def __setOrderMatcher(self):
        if self.source == 'forex_quote':
            self.orderMatcher = va.simulator.ordermatcher.forex_quoteMatcher()
        else:
            self.orderMatcher = None

    def replaceData(self, data):
        self.data = None
        self.data = data

    def getPoint(self, timestamp):
        try:
            point =  self.data.ix[timestamp]
            return {'data':point,'state':'SUCCESS'}
        except KeyError:
            return {'state':"FAIL"}



class dataEngine(object):

    def __init__(self):
        self.dataloader = simDataLoader()
        self.dataCells = []
        self.symbol_index_pair = {}

    def __getSource(self, dataName):

        if dataName in forex_quote_source:
            return 'forex_quote'
        else:
            print 'No corresponding data souce!'


    def setData(self,datalist):

        if type(datalist) is not types.TupleType and type(datalist) is not list:
            datalist = (datalist, )

        for i in range(len(datalist)):
            source = self.__getSource(datalist[i])
            self.dataCells.append(dataCell(datalist[i], source))
            self.symbol_index_pair[datalist[i]] = i

    def getPoint(self, symbol, timestamp):
        index = self.symbol_index_pair[symbol]
        return self.dataCells[index].getPoint(timestamp)

    def replaceData(self, cycle):

        timeIndex = pd.DatetimeIndex([])

        for dataCell in self.dataCells:
            beginDate = cycle['beginDate'].strftime('%Y.%m.%d')
            endDate = cycle['endDate'].strftime('%Y.%m.%d')

            temp = self.dataloader.tickerload(symbol= dataCell.symbol, source = dataCell.source,begindate = beginDate, enddate = endDate)
            temp = temp.drop_duplicates(cols = 'time')
            temp = temp[cycle['beginTime'].strftime('%Y-%m-%d %H:%M:%S'):cycle['endTime'].strftime('%Y-%m-%d %H:%M:%S')]

            dataCell.replaceData(temp)
            timeIndex = timeIndex.union(temp.index)
            temp = None

        return timeIndex

    def fillOrder(self, order):

        index = self.symbol_index_pair[order.symbol]
        trade = self.dataCells[index].orderMatcher.match(order, self.dataCells[index].data)
        return trade




