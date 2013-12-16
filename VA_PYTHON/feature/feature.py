import VA_PYTHON as va
import VD_KDB as vd
from collections import defaultdict
import ipdb
import numpy as np
import pandas as pd
#from featoperator import featgenerator

class fbase():
    '''
    fbase loads and holds all requried features for analysis
    '''

    def __init__(self):
        self.features = {} #store features
        self.featlist = defaultdict() #store the directives to generate features
        self.fgenerator = va.feature.featoperator.featgenerator() #for generating feature
        self.dloader = vd.pyapi.dataloader() #for loading data
        self.data = defaultdict() #store data for generating feature

    def datacommand(self,line):
        '''
        keyword: by
        '''

        print line
        dataname = line.split('by')[0].strip().rstrip()
        command = line.split('by')[1].strip().rstrip()
        self.addData(dataname,command)

    def featcommand(self,line):
        '''
        keyword:using,by,with
        '''

        print line
        #ipdb.set_trace()
        #get feature name
        [featname,remain] = line.split('using')
        featname = featname.strip().rstrip()

        #get data source name
        remain = remain.split('by')
        dataname = remain[0].strip().rstrip()
        remain.pop(0)

        #get all arguments
        #operation is a list of dict(a sequence of operations)
        #Each dict is a function to be applied to the time series

        operation = []
        for command in remain:
            ops = {}
            if 'with' in command:
                args = command.split('with')
                ops['name'] = args[0].strip().rstrip()
                args.pop(0)
                for arg in args:
                    [name,argexecution] = arg.split('=')
                    ops[name.strip().rstrip()] = eval(argexecution.strip().rstrip())
            else:
                ops['name'] = command.strip().rstrip()

            operation.append(ops)
        self.addFeat(featname = featname, dataname = dataname, oplist =  operation)


    def addData(self,name,command):
        if name in self.data.keys():
            print name + ' already exists! Erase the old data!'
        self.data[name] = self.dloader.load(command)
        print name, ' loaded\n'

    def addFeat(self,featname,dataname,oplist):
        '''
        load feature into fbase
        '''
        if featname in self.features.keys():
            print featname + ' already exists! Erase the old data!'
        if dataname not in self.data.keys():
            print dataname + ' not in data! Generating ' + featname + ' failed!\n'
        self.features[featname] = self.fgenerator.getfeature(operationlist=oplist,timeseries = self.data[dataname])
        print featname, ' generated\n'

    def ticketparser(self,ticketpath):
        '''
        load data, generate feature as ticket specifies.
        '''
        state = 'REST'

        with open(ticketpath) as f:
            #ipdb.set_trace()
            while state!='END':

                line = f.readline()

                if line == '':
                    break
                if line == '\n':
                    continue

                line = line.replace('\n','')

                if line == 'END':
                    state = 'END'

                if line[:4] == 'NAME':
                    print 'Begin Strategy: '+  line[4:].strip()

                if line == 'DATA':
                    state = 'DATA'
                    print '\nLoading Data...\n'
                    continue
                elif line == 'FEATURE':
                    state = 'FEATURE'
                    print '\nGenerating Features...\n'
                    continue

                if state == 'DATA':
                    self.datacommand(line)

                elif state == 'FEATURE':
                    self.featcommand(line)



