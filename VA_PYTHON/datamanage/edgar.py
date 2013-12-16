from ftplib import FTP
import os
import urllib2
import ipdb
from collections import  defaultdict
import gzip
import re
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
import nltk

DATA_ADD = os.getenv('DATA')

def getindex(beginyear, beginqtr, endyear, endqtr):
    '''Download quarterly master file from edgar database

    Args:
        beginyear, ..., endqtr (int): specify required date range

    '''
    print 'login to edgar ftp'
    ftp = FTP('ftp.sec.gov')
    print ftp.login()
    for year in range(beginyear, (endyear + 1)):
        if year == endyear:
            maxqtr = endqtr + 1
        else:
            maxqtr = 5
        if year == beginyear:
            minqtr = beginqtr
        else:
            minqtr = 1
        for qtr in range(minqtr, maxqtr):
            remotefile = 'RETR /edgar/full-index/' + str(year) + \
                    '/QTR' + str(qtr) + '/master.gz'
            localfile = DATA_ADD + '/Edgar/MasterFile/' + \
                    str(year) + 'QTR' + str(qtr) + 'master.gz'
            ftp.retrbinary(remotefile, open(localfile, 'wb').write)
            print 'download '+ str(year) + 'QTR' + str(qtr) + \
                    'master.gz'
    ftp.quit()


def ticker2CIK(ticker):
    '''Given a ticker, return corresponding CIK code
    CIK is 10 digit number'''

    string_match = 'rel="alternate"'
    url = 'http://www.sec.gov/cgi-bin/browse-edgar?company=&match=&CIK=%s&owner=exclude&Find=Find+Companies&action=getcompany' % ticker
    response = urllib2.urlopen(url)
    cik = ''
    for line in response:
        if string_match in line:
            for element in line.split(';'):
                if 'CIK' in element:
                    cik = element.replace('&amp', '')
    cik = cik[4:]
    return cik


def genCIKtable():
    '''generate a txt file that map ticker to cik'''
    tickers = set()
    nysepath = DATA_ADD + '/tickerlist/20130829/nyse20130829.txt'
    nasdaqpath = DATA_ADD + '/tickerlist/20130829/nasdaq20130829.txt'
    MSCIIndustrialPaths = '/home/brandon/edgar/Database/Industrials/IndustrialSymbolList.txt'
    tablepath = DATA_ADD + '/Edgar/cik2ticker.txt'

    def addticker(listpath):
        with open(listpath, 'rb') as f:
            for line in f:
                tickers.add(line.split('\t')[0])

    addticker(nysepath)
    addticker(nasdaqpath)
    addticker(MSCIIndustrialPaths)
    with open(tablepath, 'wb') as fout:
        for ticker in tickers:
            line = ticker + ',' + ticker2CIK(ticker) + '\n'
            print line,
            fout.write(line)
    return tickers

def getCIKdict():
    '''
    return the dictionary of CIK-ticker
    '''
    CIKtablepath = DATA_ADD + '/Edgar/cik2ticker.txt'
    CIKtable = defaultdict(str)
    with open(CIKtablepath, 'rb') as f:
        for line in f.readlines():
            line=line.rstrip('\n')
            ticker, CIK = line.split(',')
            if CIK != '':
                CIKtable[CIK] = ticker
    return CIKtable

def getTickerdict():
    '''
    return the dictionary of ticker-CIK
    '''
    cikdict = getCIKdict()
    tickerdict = defaultdict(str)
    for key, val in cikdict.items():
        tickerdict[val] = key
    return tickerdict

def GenerateCIKdirectory():
    '''
    for eac CIK/ticker, generate a directory to store
    edgar data and index file
    '''

    CIKdict = getCIKdict()
    for cik, ticker in CIKdict.items():
        filepath=DATA_ADD+'/Edgar/'+cik+"_"+ticker
        print filepath
        if not os.path.exists(filepath):
            os.makedirs(filepath)

def listmaster():
    '''
    List all master file in the disk
    '''
    #ipdb.set_trace()
    filepath = DATA_ADD + '/Edgar/MasterFile'
    masterList = os.listdir(filepath)
    masterList = sorted(masterList)
    #masterList=sorted(os.listdir(filepath))
    prevyear = ''
    for masterfile in masterList:
        currentyear = masterfile[0:4]
        currentquarter = masterfile[4:8]
        if currentyear != prevyear:
            print '\n' + currentyear + '  ' + currentquarter,
        else:
            print '  ' + currentquarter,
        prevyear = currentyear

def scanmaster(year,qtr):
    '''
    Extract 10Q/K addresss information contained in the masterfile.
    Return as a dataframe
    '''

    masterfilepath = DATA_ADD + '/Edgar/MasterFile/' + \
            str(year) + 'QTR' + str(qtr) + 'master.gz'
    CIKdict = getCIKdict()
    forms = pd.DataFrame(columns=['CIK','Ticker','Date','Type','Address'])
    f = gzip.open(masterfilepath, 'rb')
    for line in f.readlines():
        line = line.rstrip('\n')
        if line[-4:] == '.txt':
            cik, name, formtype, formdate, address = line.split('|')
            if re.search('^10.*$', formtype):
                if cik.zfill(10) in CIKdict:
                    pdline=pd.DataFrame(
                        {'CIK':[cik.zfill(10)],
                        'Ticker':[CIKdict[cik.zfill(10)]],
                        'Date':[parse(formdate)],
                        'Type':[formtype],
                        'Address':[address]},
                        columns=['CIK','Ticker','Date','Type','Address'])
                    forms = pd.concat([forms,pdline])
    f.close()
    return forms

def readindex(indexfilepath):
    '''
    return all existing entries in an index file as dataframe
    '''

    if os.path.exists(indexfilepath):
        entries=pd.read_table(indexfilepath,sep=',')
        return entries
    else:
        return "EMPTY"

def updateindexfile(year,qtr):
    '''
    Extract information from master file and  update the index file.
    '''
    CIKdict = getCIKdict()
    print 'Scanning master file...'

    forms = scanmaster(year,qtr)
    cikset = set(forms['CIK'])

    for cik in cikset:
        cikform = forms[forms['CIK'] == cik]
        indexfilepath = DATA_ADD + '/Edgar/' + str(cik) + \
                '_' + str(CIKdict[cik]) + '/' + 'index.txt'
        if not os.path.exists(indexfilepath):
            print 'Index file does not exist. Create ',indexfilepath
            cikform.to_csv(indexfilepath,sep=',',header=True, index = False)
        else:
            print 'Updating ',indexfilepath
            indexfile = pd.read_table(indexfilepath,sep = ',',
                                      dtype={'CIK':'S10',})
            indexfile['Date'] = indexfile['Date'].apply(parse)
            indexfile = pd.concat([indexfile,cikform])
            indexfile = indexfile.drop_duplicates()
            indexfile = indexfile.sort('Date')
            indexfile.to_csv(indexfilepath,sep=',',header=True, index = False)


def updateCoreIndex():
    '''
    Core index file stores 10QK filing information of all stocks
    Update core index file based on the indexfile of each stock
    '''
    coreindexpath = DATA_ADD + '/Edgar/coreindex.txt'
    coreindex = pd.DataFrame(columns=['CIK','Ticker','Date','Type','Address'])
    CIKdict = getCIKdict()
    for cik in CIKdict:
        indexfilepath = DATA_ADD + '/Edgar/' + str(cik) + \
                '_' + str(CIKdict[cik]) + '/' + 'index.txt'
        if os.path.exists(indexfilepath):
            indexfile = pd.read_table(indexfilepath,sep = ',',
                                        dtype={'CIK':'S10',})
            indexfile['Date'] = indexfile['Date'].apply(parse)
            coreindex = pd.concat([indexfile,coreindex])
    coreindex = coreindex.drop_duplicates()
    coreindex = coreindex.sort('Date')
    coreindex.to_csv(coreindexpath,sep=',',header=True, index = False)


def downloadform(_ftp,remotefile,localfile):
    '''Download 10QK form  from edgar'''
    ftp = _ftp
    remotefile = 'RETR /'+ remotefile
    if not os.path.exists(localfile + '.gz'):
        #ipdb.set_trace()
        ftp.retrbinary(remotefile, open(localfile, 'wb').write)
        f_in = open(localfile,'rb')
        f_out = gzip.open(localfile+'.gz','wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(localfile)
        print datetime.now(),': ',localfile + ' downloaded'
    else:
        print localfile + '.gz already exists'

def updateTickerForm(ticker,ftp_ = None):
    '''
    download the 10 form of the ticker.
    if already downloaded, skip
    '''
    ftpQuit = False
    ftp = None
    if ftp_ == None:
        ftp = FTP('ftp.sec.gov')
        ftp.login()
        ftpQuit = True
    else:
        ftp = ftp_

    tickerdict = getTickerdict()
    if ticker in tickerdict.keys():
        cik = tickerdict[ticker]
        indexfilepath = DATA_ADD + '/Edgar/' + str(cik) + \
                '_' + str(ticker) + '/index.txt'
        if os.path.exists(indexfilepath):
            indexfile = pd.read_table(indexfilepath,sep = ',',
                                      dtype = {'CIK':'S'})
            indexfile['Date'] = indexfile['Date'].apply(parse)
            for row in indexfile.iterrows():
                formdate = row[1]['Date']
                formtype = row[1]['Type']
                formtype = formtype.replace('/','-')
                localfile = DATA_ADD + '/Edgar/' + str(cik) + \
                        '_' + str(ticker) + '/' + str(cik) + '_' + \
                        str(ticker) + '_' + formdate.strftime('%Y%m%d') + \
                        '_' + formtype + '.txt'
                remotefile = row[1]['Address']
                downloadform(ftp,remotefile,localfile)
        else:
            print 'index file doest not exist!'
    else:
        print ticker,' does not exist!'
    if ftpQuit == True:
        ftp.quit()

def updateAll(ftp_ = None):
    '''
    download 10KQ forms of all ticker
    '''
    ftpQuit = False
    ftp = None
    if ftp_ == None:
        ftp = FTP('ftp.sec.gov')
        ftp.login()
        ftpQuit = True
    else:
        ftp = ftp_

    tickerdict = getTickerdict()
    for ticker in tickerdict:
        print 'updating forms of ',ticker
        updateTickerForm(ticker)

    print 'Update complete'
    if ftpQuit == True:
        ftp.quit()

def checkEmpty(symbolList):
    '''
    return ticker list with empty index file
    '''
    tickerdict = getTickerdict()
    NotInTickerDict = []
    NoIndexFile = []
    for symbol in symbolList:
        if symbol not in tickerdict.keys():
            NotInTickerDict.append(symbol)
        else:
            cik = tickerdict[symbol]
            indexfilepath = DATA_ADD + '/Edgar/' + str(cik) + \
                '_' + str(symbol) + '/index.txt'
            if not os.path.exists(indexfilepath):
                NoIndexFile.append(symbol)
    result = {'NoSymbol':NotInTickerDict,
              'NoIndex':NoIndexFile}
    return result

def GenerateBOW(raw):
    '''
    generate bow from raw input
    '''
    raw = nltk.clean_html(raw)
    regexp = r'[a-zA-Z]+'
    words = re.findall(regexp, raw)
    words = [word.lower() for word in words]
    words = [word for word in words if not word in nltk.corpus.stopwords.words('english')]
    words = [word for word in words if len(word) > 2]
    words = [word for word in words if len(word) < 20]
    lemmatizer = nltk.WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word ) for word in words]
    fcounts  = defaultdict(int)
    for word in words:
        fcounts[word] += 1
    return fcounts


####DEPRECIATED####
def extractMDA_new(raw):
    '''
    Test new way of extract MDA
    '''
    #ipdb.set_trace()
    raw = nltk.clean_html(raw)
    #replace special characters
    raw = raw.replace('&#146;','\'')
    raw = raw.replace('&npsp;',' ')
    raw = raw.replace('\n',' ')

    #If there is table of contents, cut it
    contentsIndex = raw.lower().find('table of contents')
    if contentsIndex != -1:
        raw = raw[contentsIndex+2000:]

    beginPatternList = list()
    beginPatternList.append(r'ITEM.{,10}MANAGEMENT\'S {,3}DISCUSSION {,3}AND {,3}ANALYSIS')
    beginPatternList.append(r'ITEM.{,10}Management\'s {,3}Discussion {,3}[Aa]nd {,3}Analysis')
    beginPatternList.append(r'Item.{,10}MANAGEMENT\'S {,3}DISCUSSION {,3}AND {,3}ANALYSIS')
    beginPatternList.append(r'Item.{,10}Management\'s {,3}Discussion {,3}[Aa]nd {,3}Analysis')
    beginPatternList.append(r'MANAGEMENT\'S {,3}DISCUSSOIN{,3}AND {,3}ANALYSIS')
    beginPatternList.append(r'Management\'s {,3}Discussion{,3}[Aa]nd {,3}Analysis')
    beginPatternList.append(r'FINANCIAL {,3}REVIEW')
    beginPatternList.append(r'Financial {,3}Review')

    beginPattern = list()
    beginPatternIndex = -1

    for i in range(len(beginPatternList)):
        beginPattern = re.findall(beginPatternList[i],raw)
        if len(beginPattern) == 1:
            #Locate exactly
            beginPatternIndex = raw.find(beginPattern[0])
            break
        elif len(beginPattern) > 1:
            #multiple locations case
            locations = [m.start() for m in re.finditer(beginPattern[0],raw)]
            for loc in locations:
                #rule out reference
                if ' in' in raw[loc-5:loc]:
                    break
                else:
                    #find the exact location
                    beginPatternIndex = loc
                    break
        if beginPatternIndex != -1:
            #if begin pattern found, stop for loop
                break

def extractMDA(raw):
    '''
    raw:string
    clean a raw 10qk form and extract MDA out of it.
    '''

    #Should deal with the situation where there is no table of contents

    #ipdb.set_trace()
    raw = nltk.clean_html(raw)
    #replace special characters
    raw = raw.replace('&#146;','\'')
    raw = raw.replace('&npsp;',' ')
    raw = raw.replace('\n',' ')
    contentsIndex = raw.lower().find('table of contents')
    if contentsIndex != -1:
        return extractMDA_with_contents(raw,contentsIndex)
    else:
        return extractMDA_without_contents(raw)

def extractMDA_with_contents(raw,contentsIndex):
    '''
    Extract MDA from reports that have table of contents
    '''
    #get index of first appearnce of MDA keyword
    mdaoccur = re.findall('Management\'s {,5}Discussion {,5}and {,5}Analysis',raw[contentsIndex:(contentsIndex+5000)])
    if len(mdaoccur) != 0:
        mdacontentpattern = mdaoccur[0]
    else:
        errmsg = 'Cannot find mda content pattern in table of contents'
        print errmsg
        return (-1,errmsg)

    mdaIndex1 = raw.find(mdacontentpattern)

    #get the item numbering of MDA
    beforemda1 = raw[:mdaIndex1]
    itemindex = beforemda1.lower().rfind('item')
    mdaItemNum = re.findall('[0-9]+',raw[itemindex:mdaIndex1])

    if len(mdaItemNum)!=0:
        mdaItemNum = int(mdaItemNum[0])
        nextItemNum = mdaItemNum + 1
    else:
        errmsg = "Cannot find item number of MDA in table of contents"
        print errmsg
        return (-1,errmsg)

    #get the title the item right after MDA
    #search for the first appearance of item X+1 in the text after MDA return mdaItemNum
    nextItemPattern = 'item ' + str(nextItemNum)
    nextItemIndex = raw[mdaIndex1:(mdaIndex1+500)].lower().find(nextItemPattern)


    #some patterns are not capitalized,should modify the pattern
    mdaBeginPattern1 = 'ITEM ' + str(mdaItemNum)
    mdaBeginPattern2 = 'Item ' + str(mdaItemNum)
    mdaBeginPattern3 = 'Management\'s Discussion and Analysis'
    mdaEndPattern1 = 'ITEM ' + str(nextItemNum)
    mdaEndPattern2 = 'Item ' + str(nextItemNum)

    mdaBeginIndex1 = raw[(mdaIndex1+500):].find(mdaBeginPattern1)
    mdaBeginIndex2 = raw[(mdaIndex1+500):].find(mdaBeginPattern2)
    mdaBeginIndex3 = raw[(mdaIndex1+500):].find(mdaBeginPattern3)

    if mdaBeginIndex1 != -1:
        mdaBeginIndex = mdaBeginIndex1
    elif mdaBeginIndex2 != -1:
        mdaBeginIndex = mdaBeginIndex2
    elif mdaBeginIndex3 != -1:
        mdaBeginIndex = mdaBeginIndex3
    else:
        errmsg = 'Cannot find MDA beginning pattern in main body'
        print errmsg
        return (-2,errmsg)

    if nextItemIndex != -1:
        # there is item x+1
        nextItemIndex += (mdaIndex1 + 500)
        mdaEndIndex1 = raw[nextItemIndex:].find(mdaEndPattern1)
        mdaEndIndex2 = raw[nextItemIndex:].find(mdaEndPattern2)


        if mdaEndIndex1 != -1:
            mdaEndIndex = mdaEndIndex1
        elif mdaEndIndex2 != -1:
            mdaEndIndex = mdaEndIndex2
        else:
            errmsg = 'MDA ending pattern found in table of contents, but ending pattern Cannot be found in main body'
            print errmsg
            return (-3,errmsg)
        #ipdb.set_trace()
        mdaBeginIndex += (mdaIndex1 + 500)
        mdaEndIndex += nextItemIndex
        mda = raw[mdaBeginIndex:mdaEndIndex]
    else:
        mdaBeginIndex += (mdaIndex1+500)
        mda = raw[mdaBeginIndex:]
    print 'Successful'
    return (0,mda)

def extractMDA_without_contents(raw):
    '''
    extract MDA from report that does not have table of contents
    '''

    #ipdb.set_trace()
    beginPattern1 = re.findall(r'ITEM.{,20}Management\'s Discussion and Analysis',raw)
    beginPattern2 = re.findall(r'Management\'s Discussion and Analysis',raw)
    beginPattern3 = re.findall(r'MANAGEMENT\'S DISCUSSION AND ANALYSIS',raw)
    beginPattern4 = re.findall(r'FINANCIAL REVIEW',raw)
    beginPattern5 = re.findall(r'Financial Review',raw)


    if len(beginPattern1)!=0:
        beginPattern = beginPattern1[0]
    elif len(beginPattern2) != 0:
        beginPattern = beginPattern2[0]
    elif len(beginPattern3) != 0:
        beginPattern = beginPattern3[0]
    elif len(beginPattern4) != 0:
        beginPattern = beginPattern4[0]
    elif len(beginPattern5) != 0:
        beginPattern = beginPattern5[0]
    else:
        errmsg = "No table of contents. Cannot find beginning pattern."
        print errmsg
        return (-1,errmsg)

    beginPatternIndex = raw.find(beginPattern)
    endPattern1 = 'PART'
    endPattern2 = 'ITEM'
    endPattern3 = 'Item'

    endPatternIndex1 = raw[beginPatternIndex:].find(endPattern1)
    endPatternIndex2 = raw[beginPatternIndex:].find(endPattern2)
    endPatternIndex3 = raw[beginPatternIndex:].find(endPattern3)

    if endPatternIndex1 != -1:
        endPatternIndex = endPatternIndex1 + beginPatternIndex
        print 'Successful'
        return (0,raw[beginPatternIndex:endPatternIndex])

    elif endPatternIndex2 != -1:
        endPatternIndex = endPatternIndex2 + beginPatternIndex
        print 'Successful'
        return (0,raw[beginPatternIndex:endPatternIndex])
    elif endPatternIndex3 != -1:
        endPatternIndex = endPatternIndex3 + beginPatternIndex
        print 'Successful'
        return (0,raw[beginPatternIndex:endPatternIndex])
    else:
        #Assume the MDA is the last section of report
        print 'Successful'
        return (0,raw[beginPatternIndex:])

def gettickerMDA(ticker):
    '''
    based on the index file of a ticker,read in every 10qk filing,
    extract mda from the filing and save to the same directory
    '''

    tickerdict = getTickerdict()
    if ticker in tickerdict.keys():
        cik = tickerdict[ticker]
        indexfilepath = DATA_ADD + '/Edgar/' + str(cik) + \
                '_' + str(ticker) + '/index.txt'
        mdaindexfilepath = DATA_ADD + '/Edgar/' + str(cik) + \
                '_' + str(ticker) + '/mdaindex.txt'

        if os.path.exists(indexfilepath):
            indexfile = pd.read_table(indexfilepath,sep = ',',
                                      dtype = {'CIK':'S'})
            indexfile['Date'] = indexfile['Date'].apply(parse)
            mdaindexfile = indexfile.copy()
            mdaindexfile = mdaindexfile.rename(columns = {'Address':'MDA_state'})
            #ipdb.set_trace()
            for row in indexfile.iterrows():
                formdate = row[1]['Date']
                formtype = row[1]['Type']
                formtype = formtype.replace('/','-')

                localfile = DATA_ADD + '/Edgar/' + str(cik) + \
                        '_' + str(ticker) + '/' + str(cik) + '_' + \
                        str(ticker) + '_' + formdate.strftime('%Y%m%d') + \
                        '_' + formtype + '.txt.gz'
                mdafile = DATA_ADD + '/Edgar/' + str(cik) + \
                            '_' + str(ticker) + '/' + str(cik) + '_' + \
                        str(ticker) + '_' + formdate.strftime('%Y%m%d') + \
                        '_' + formtype + '_MDA.txt.gz'

                f_in = gzip.open(localfile,'rb')
                raw = f_in.read()
                mdastate,content = extractMDA(raw)

                if mdastate == -1:
                    mdaindexfile['MDA_state'][row[0]] = content
                if mdastate == -2:
                    mdaindexfile['MDA_state'][row[0]] = content
                if mdastate == -3:
                    mdaindexfile['MDA_state'][row[0]] = content
                if mdastate == 0:
                    mdaindexfile['MDA_state'][row[0]] = 'Successful'
                    f_out = gzip.open(mdafile,'wb')
                    f_out.write(content)
                    f_in.close()
                    f_out.close()
            mdaindexfile.to_csv(mdaindexfilepath,sep=',',header=True, index = False)
        else:
            print 'index file doest not exist!'
    else:
        print ticker,' does not exist!'


