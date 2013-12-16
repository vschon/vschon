import urllib
import csv
from datetime import datetime,date,time
from dateutil.relativedelta import relativedelta
import os
import zipfile

HOMEADDRESS="/nv/hcoc1/ryang40/data"
data_addr = os.getenv('DATA')
temp_addr = data_addr + '/forex_temp/'

def GetData(url,address):
    urllib.urlretrieve(url,address)

####TrueFX Data####

def GetTrueFX_MilliQuote(dt,ticker):
    url="https://www.truefx.com/dev/data/"+dt.strftime("%Y")+"/"+dt.strftime("%B").upper()+"-"+dt.strftime("%Y")+"/"+ticker.upper()+"-"+dt.strftime("%Y")+"-"+dt.strftime("%m")+".zip"
    address=temp_addr+ticker.upper()+dt.strftime("%Y")+dt.strftime("%m")+".zip"
    if not os.path.exists(address):
        GetData(url,address)
        print address + ' downloaded'
    else:
        print address + ' already exists'

def processData(dt,ticker):
    '''
    process the downloaded data into correct format for kdb disgest
    '''

    address=temp_addr+ticker.upper()+dt.strftime("%Y")+dt.strftime("%m")+".zip"
    oldcsv_addr=temp_addr + ticker.upper() + '-' + dt.strftime("%Y") + '-' + dt.strftime("%m") + '.csv'
    newcsv_addr = temp_addr + ticker.upper() + dt.strftime("%Y") + dt.strftime("%m")+ '.csv'

    fzip = zipfile.ZipFile(address)
    fzip.extractall()
    fcsv = open(oldcsv_addr,'rb')
    raw = fcsv.read()
    #AUD/JPY --> AUDJPY
    raw = raw.replace('/','')

    fout = open(newcsv_addr,'w')
    fout.write(raw)
    fcsv.close()
    fout.close()
    os.remove(oldcsv_addr)


def GetTrueFX_Batch(startYear,startMonth,endYear,endMonth):
    startDate=datetime(startYear,startMonth,1)
    endDate=datetime(endYear,endMonth,1)

    reader=csv.reader(open(temp_addr+"0Forex_ticker_list.csv","rb"))
    downloadList=list(reader)
    listLength=len(downloadList)

    for i in range(0,listLength):
        ticker=downloadList[i][0]
        currentDate=startDate
        while(currentDate<=endDate):
            GetTrueFX_MilliQuote(currentDate,ticker)
            processData(currentDate,ticker)
            currentDate=currentDate+relativedelta(months=1)

def RemoveBadZip_TrueFx(startYear,startMonth,endYear,endMonth):

    startDate=datetime(startYear,startMonth,1)
    endDate=datetime(endYear,endMonth,1)
    reader=csv.reader(open(HOMEADDRESS+"/Vdata/Milli_Quote_FX/Milli_Quote_FX_List.csv","rb"))
    downloadList=list(reader)
    listLength=len(downloadList)
    for i in range(0,listLength):
        ticker=downloadList[i][0]
        currentDate=startDate
        while(currentDate<=endDate):
            address=HOMEADDRESS+"/Vdata/Milli_Quote_FX/temp/"+ticker.upper()+currentDate.strftime("%Y")+currentDate.strftime("%m")+".zip"
            if(os.path.isfile(address)==True):
                os.remove(address)
            currentDate=currentDate+relativedelta(months=1)


