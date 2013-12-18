import VD_DATABASE as vd
import os
import mechanize
import datetime as dt
import ipdb
import zipfile
from dateutil.parser import parse
from dateutil import rrule
import dateutil
import nltk

#DATA_ADD = os.getenv('DATA')
DATA_ADD = '/media/Data/testData'
tempAddress = os.path.join(DATA_ADD, 'temp')



class forex_quoteManager(vd.kdbAPI.dataloader):
    '''
    Manage the database forex_quote
    '''

    def __init__(self):
        vd.kdbAPI.dataloader.__init__(self)
        try:
            self.forex_quoteAddress = os.path.join(DATA_ADD,'forex_taqDB','forex_taq')
            self.qDirective('\l ' + self.forex_quoteAddress)
        except:
            print 'Warning, Database is not populated yet!'
            print 'Please execute InitialzeDatabase() method before using other functions'
        self.populateKDBAddress = os.path.join(os.path.dirname(__file__),'populate_forex_quote.q')
        self.symbolList = ['AUDJPY',
                           'AUDNZD',
                           'AUDUSD',
                           'CADJPY',
                           'CHFJPY',
                           'EURCHF',
                           'EURGBP',
                           'EURJPY',
                           'EURUSD',
                           'GBPJPY',
                           'GBPUSD',
                           'NZDUSD',
                           'USDCAD',
                           'USDCHF',
                           'USDJPY']
        self.br = mechanize.Browser()
        self.dataURL = 'http://www.truefx.com/dev/data'

    def update(self,month = None):
        '''
        update forex_quote database

        Parameters
        ----------
        month: string, optional
            the month of data to be updated
            if month == None, then manager will check if there is new data in
            TrueFX and update accordingly;
            if monthe = '2000.08', then manger will look up for the data in TrueFX
            and update the data of the month

        '''

        if month != None:
            updateList = [parse((month + '.01')),]
        else:
            updateList = self.checkNew()

        for filedate in updateList:
            month = filedate.strftime(format = '%Y.%m')
            for symbol in self.symbolList:
                self.__updateSingle(symbol, month)

    def checkNew(self):
        '''
        check for new data on TrueFX

        Returns
        -------
        updateList: list
            list of filenames to updated
        '''

        latestLocalMonth = self.summary()
        latestLocalDate = dt.datetime(day = 1, month = int(latestLocalMonth[-2:]), year = int(latestLocalMonth[:4]))
        latestLocalDate = latestLocalDate + dateutil.relativedelta.relativedelta(months = 1)

        dataHTML = self.br.open(self.dataURL).read()
        yearList = nltk.clean_html(dataHTML).split('\n')
        yearList = [int(item[1:5]) for item in yearList if '20' in item]
        latestYear = max(yearList)

        yearURL = self.dataURL + '/' + str(latestYear)
        monthList = nltk.clean_html(self.br.open(yearURL).read()).split('\n')
        monthList = [month for month in monthList if ('-' + str(latestYear)) in month]
        latestMonth = len(monthList)

        latestRemoteDate = dt.datetime(day = 1, month = latestMonth, year = latestYear)

        updateList = list(rrule.rrule(rrule.MONTHLY, dtstart = latestLocalDate, until = latestRemoteDate))

        print 'The following months needs updated:\n'
        i = 1
        for month in updateList:
            print month.strftime(format = '%Y.%m') + '  ',
            if i % 5 == 0:
                print '\n',
            i += 1
        print '\n'

        return updateList




    def __updateSingle(self, symbol, filedate):
        '''
        download corresponding file, and populate it into the database

        Parameter
        ---------
        symbol: string
        filedate: string
            in format '2000.01'
        '''

        initialYear = filedate[:4]
        initialMonth = filedate[5:]
        monthAlpha = parse(filedate + '.01').strftime('%B').upper()

        filename = symbol + '-' + str(initialYear) + '-' + initialMonth + '.zip'

        remoteAdd = 'http://www.truefx.com/dev/data/' + str(initialYear) + '/' + monthAlpha +\
                '-' + str(initialYear) + '/' + filename
        localAdd = os.path.join(tempAddress, filename)
        result = self.br.retrieve(remoteAdd,localAdd)[0]
        print result + 'downloaded'

        csvAddress = self.__processData(localAdd)

        filedate = '2009.05'
        command = 'q ' + self.populateKDBAddress + ' ' + filedate + ' ' + symbol
        os.system(command)
        os.remove(csvAddress)


    def InitializeDatabase(self):
        '''
        Initialize database, only used in the first time
        '''

        if not os.path.exists(tempAddress): os.mkdir(tempAddress)
        filedate = '2009.05'
        for symbol in self.symbolList:
            self.__updateSingle(symbol, filedate)

    def __processData(self,localAddress):
        '''
        Parameter
        ---------
        localAddress: string
            path to the target file

        Return
        ------
        csvAddress: string
            path to the generated csv file
        '''

        csvAddress = localAddress.replace('zip','csv')
        csvAddress = csvAddress.replace('-','')

        fzip = zipfile.ZipFile(localAddress)
        for filename in fzip.namelist():
            raw = fzip.read(filename)
            raw = raw.replace('/','')

        fzip.close()
        with open(csvAddress,'w') as fout:
            fout.write(raw)
        os.remove(localAddress)
        return csvAddress

    def summary(self):
        '''
        list symbol list and date range of forex_quote database

        Returns
        -------
        lastmonth: string
            format = '2001.01'
        '''
        sampleAddress = os.path.join(DATA_ADD,'forex_taqDB','EURUSD')
        partxtAddress = os.path.join(DATA_ADD,'forex_taqDB','forex_taq','par.txt')
        date_range = sorted(os.listdir(sampleAddress))
        month_range = sorted(set([x[:7] for x in date_range]))
        lastMonth = month_range[-1]
        symbol_range = []
        with open(partxtAddress,'rb') as f:
            for line in f:
                symbol_range.append(line[-7:-1])

        print 'All symbols include:'
        for i in range(len(symbol_range)):
            print symbol_range[i] + '  ',
            if (i + 1) % 4 == 0:
                print ' '

        print '\n\nMonth ranges include:'
        for i in range(len(month_range)):
            print month_range[i],
            if month_range[i][-2:] == '12':
                print ''

        print '\n\nLast Month is ' + lastMonth
        return lastMonth

    def loadPrice(self, symbol, beginDate, endDate = None):
        '''
        load price from KDB into memory

        Parameters
        ----------
        symbol: string
            uppercase of the symbol name
        beginDate: string
            format: '2000.01.01'
        endDate: string, optional
            if not specified, then endDate = beginDate

        Returns
        -------
        price: DataFrame
        '''
        return self.tickerload(source = 'forex_quote', symbol = symbol, beginDate = beginDate, endDate = endDate)

