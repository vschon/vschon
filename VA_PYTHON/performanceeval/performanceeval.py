import pandas as pd
import numpy as np

def rmse(pred,actual):
    rmse = np.sqrt(np.mean(np.square(actual-pred)))
    return rmse

def hitrate(pred,actual):
    '''
    return correct percentage of forecast
    '''

    prod=pred*actual
    return float(sum(prod>0))/float(sum(pred!=0))

def featureeval(pred,actual):
    error=rmse(pred,actual)
    correlation=np.corrcoef(pred,actual)[0,1]
    correctrate=hitrate(pred,actual)

    return {'rmse':error,'correlation':correlation,'hitrate':correctrate}

