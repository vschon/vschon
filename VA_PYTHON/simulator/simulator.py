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

