from collections import defaultdict
import VA_PYTHON as va
import VD_KDB as vd
import ipdb


class featgenerator():
    '''
    hold all available operators and generate features
    '''

    def __init__(self):
        self.operations = defaultdict()

        print 'Initializing operators...'

        #ALL FEATURES LISTED HERE
        self.operations['hawkes'] = va.models.hawkes.hawkesfeat

    def getoperator(self,opname):
        return self.operations[opname]

    def getfeature(self,operationlist,timeseries):
        '''
        Generate a feature time series
        operations: list of dict

        each operation is a dict
        operations = [
                {'name':'hawkes',
                    'par1':2},
                {'name':'normalize',
                    'par1':(1,2,3),
                    'par2':3}
                ]
        '''
        #ipdb.set_trace()
        for ops in operationlist:
            if ops['name'] in self.operations.keys():
                opname = ops['name']
                operator = self.getoperator(opname)
                timeseries = operator(timeseries,args = ops)
            else:
                print 'Operation '+ opname + ' not defined!'
                break

        return timeseries




