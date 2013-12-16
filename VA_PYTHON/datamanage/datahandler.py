import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
import types

class Sender(object):

    '''
    Sender-> dispatched messages to registered callables
    '''

    def __init__(self):
        self.listeners = {}

    def register(self, listerner, events = None):
        '''
        lister: external listener function
        '''
        if events is not None and type(events) not in (types.TupleType,types.ListType):
            events = (events,)
        self.listeners[listerner]= events

    def dispatch(self,event = None, msg = None):
        '''
        notify listeners
        '''

        for listener,events in self.listeners.items():
            if events is None or event is None or event in events:
                    listener(self,event,msg)

class ExampleListener(object):
    def __init__(self,name=None):
        self.name = name

    def method(self,sender,event,msg=None):
        print "[{0}] got event {1} with message {2}".format(self.name,event,msg)


