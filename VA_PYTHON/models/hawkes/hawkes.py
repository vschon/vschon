import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from scipy.optimize import minimize
import getR
import datetime as dt
import os
import VD_DATABASE as vd
import VA_PYTHON as va
import ipdb

#utility function

def delta2second(delta):
    '''
    convert a timedelta to float number (in seconds)
    '''
    return delta.total_seconds()

Vdelta2second = np.vectorize(delta2second)

def second2delta(second):
    return timedelta(0,second)

Vsecond2delta = np.vectorize(second2delta)

def df2np(raw):
    '''
    transform raw dataframe to numpy representation
    output:
        ndarray with col time(begin with 0), price mark, rate +, rate -
    '''
    #ipdb.set_trace()
    #transform time to seconds beginning at t=0
    value = raw.values
    anchor = value[-1]

    # get index of entires with no price change
    index = np.where((value[1:,1]==value[0:-1,1])==True)
    value = np.delete(value,index,0)
    n = value.shape[0] - 1
    newValue = np.append(np.diff(value,axis=0),np.zeros((n,2)),axis = 1)
    newValue[:,0] = Vdelta2second(newValue[:,0])
    newValue[:,1] = np.sign(newValue[:,1])
    #remove items with no price change
    return (newValue[newValue[:,1] != 0],anchor)

def np2df(data,anchor,ticksize = 0.0001):
    '''
    convert to np representation to df price sequence
    '''
    value = np.cumsum(data[:,:2],axis=0)
    value = value.astype(object,copy=False)
    value[:,0] = Vsecond2delta(value[:,0])
    value[:,1] = value[:,1] * ticksize
    value = value + anchor
    return pd.DataFrame(value,columns=['time','quantity'])


class simulator:

    def __init__(self,theta=(0.5,0.5,0.5,0.5,0.5,0.5,1,1),scale = 0.001):
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:]).reshape(2,1)
        self.scale = scale
        self.history = pd.DataFrame()
        self.rateCalculated = False
        self.historydata = None
        self.anchor = None

    def setparam(self,theta,scale):
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:]).reshape(2,1)
        self.scale = scale

    def sethistory(self,history = pd.DataFrame()):
        #ipdb.set_trace()
        self.history = history
        if self.history.shape[0] != 0:
            self.historydata,self.anchor = df2np(self.history)
            self.historydata = self.historyrate(self.historydata)

    def rate(self,time,prev_index,data):
        '''
        Calculate the rate at time t
        '''
        ratevalue = np.zeros((2,1))
        if(prev_index<0):
            ratevalue = self.mu
        else:
            ratevalue[0,0] = self.mu[0,0] + (data[prev_index,2] - self.mu[0,0])/np.exp(self.beta[0,0]*time)
            ratevalue[1,0] = self.mu[1,0] + (data[prev_index,3] - self.mu[1,0])/np.exp(self.beta[1,0]*time)
        return ratevalue

    def historyrate(self,data):
        '''
        Calculate the historic rate
        '''
        dataNum = data.shape[0]
        for i in range(dataNum):
            ratevalue = self.rate(data[i,0],i-1,data)
            if data[i,1] == 1.0:
                data[i,2:4] = (ratevalue + self.alpha[:,0].reshape(2,1)).reshape(2)
            else:
                data[i,2:4] = (ratevalue + self.alpha[:,1].reshape(2,1)).reshape(2)
        self.rateCalculated = True
        return data

    def simulate(self,dataNum=10):
        if self.history.shape[0] == 0:
            totalIndex = -1
            subIndex1 =0
            subIndex2 =0
            maxIntensity = np.sum(self.mu)
            self.anchor = np.array([datetime.now(),0.0])
            #first event
            s = np.random.exponential(1/maxIntensity)
            data = np.zeros((dataNum,4))
            # attribution test
            randomD = np.random.uniform()
            if randomD<=self.mu[0,0]/maxIntensity:
                data[0,0] = s
                data[0,1] = 1.0
                data[0,2:4] = (self.mu + self.alpha[:,0].reshape(2,1)).reshape(2)
                subIndex1+=1
                totalIndex+=1
            else:
                data[0,0] = s
                data[0,1] = -1.0
                data[0,2:4] = (self.mu + self.alpha[:,1].reshape(2,1)).reshape(2)
                subIndex2+=1
                totalIndex+=1
            endIndex = dataNum
        else:
            #if history is provided, continue simulation after history
            totalIndex = self.historydata.shape[0]-1
            subIndex1 = sum(self.historydata[:,1] == 1.0)
            subIndex2 = sum(self.historydata[:,1] == -1.0)

            data = np.append(self.historydata,np.zeros((dataNum,4)),axis=0)
            endIndex = dataNum + totalIndex + 1

        #general routine
        for i in range((totalIndex+1),endIndex):
            ratevalue = self.rate(data[totalIndex,0],totalIndex,data)
            maxIntensity = np.sum(ratevalue)
            cum_s = 0.0
            while(True):
                s = np.random.exponential(1/maxIntensity) + cum_s
                ratevalue = self.rate(s,totalIndex,data)
                intensity_s = np.sum(ratevalue)
                randomD = np.random.uniform()

                if randomD <= intensity_s/maxIntensity:
                    totalIndex+=1
                    data[totalIndex,0] = s
                    if randomD <= ratevalue[0,0]/maxIntensity:
                        subIndex1 += 1
                        data[totalIndex,1] = 1.0
                        data[totalIndex,2:4] = (ratevalue + self.alpha[:,0].reshape(2,1)).reshape(2)
                    else:
                        subIndex2+=1
                        data[totalIndex,1] = -1.0
                        data[totalIndex,2:4] = (ratevalue + self.alpha[:,1].reshape(2,1)).reshape(2)
                    break
                else:
                    maxIntensity = intensity_s
                    cum_s += s
        if self.history.shape[0] == 0:
            price = np2df(data,self.anchor,self.scale)
            return price,data
        else:
            price = np2df(data[-dataNum:,:2],self.anchor,self.scale)
            return price,data


def getR11(N,beta1,pos):
    R11 = np.zeros((N,1))
    for i in range(1,N):
        R11[i,0] = (1+R11[i-1,0])*np.exp(-beta1*(pos[i,0]-pos[i-1,0]))
    return R11

def getR12(N,M,beta1,pos,neg):
    R12 = np.zeros((N,1))
    for i in range(1,N):
        tempsum=0.0
        for j in range(M):
            if neg[j,0] >= pos[i,0]:
                break
            if neg[j,0] >= pos[i-1,0] and neg[j,0] < pos[i,0]:
                tempsum += np.exp(-beta1*(pos[i,0] - neg[j,0]))
        R12[i,0] = R12[i-1,0]*np.exp(-beta1*(pos[i,0]-pos[i-1,0])) + tempsum
    return R12

def getR21(N,M,beta2,pos,neg):
    R21 = np.zeros((M,1))
    for j in range(1,M):
        tempsum=0.0
        for i in range(N):
            if pos[i,0] > neg[j,0]:
                break
            if pos[i,0] >= neg[j-1,0] and pos[i,0] < neg[j,0]:
                tempsum += np.exp(-beta2*(neg[j,0]-pos[i,0]))
        R21[j,0] = R21[j-1,0]*np.exp(-beta2*(neg[j,0]-neg[j-1,0])) + tempsum
    return R21

def getR22(M,beta2,neg):
    R22 = np.zeros((M,1))
    for j in range(1,M):
        R22[j,0] = (1+R22[j-1,0])*np.exp(-beta2*(neg[j,0]-neg[j-1,0]))
    return R22


def compensator(theta,data):
    '''
    Calculate the compensator for a given bivariate hawkes process sequence
    '''
    mu = np.array(theta[:2]).reshape(2,1)
    alpha = np.array(theta[2:6]).reshape(2,2)
    beta = np.ones((2,1))
    data[:,0] = np.cumsum(data[:,0])
    pos = data[data[:,1] == 1.0,0].reshape(-1,1)
    neg = data[data[:,1] == -1.0,0].reshape(-1,1)
    pos = pos.astype(float,copy=False)
    neg = neg.astype(float,copy=False)
    N = pos.shape[0]
    M = neg.shape[0]
    T = data[-1,0]
    A11 = getR.getR11(N,beta[0,0],pos)
    A12 = getR.getR12(N,M,beta[0,0],pos,neg)
    A21 = getR.getR21(N,M,beta[1,0],pos,neg)
    A22 = getR.getR22(M,beta[1,0],neg)

    Lambda1 = np.zeros((N-1,1))
    Lambda2 = np.zeros((M-1,1))

    for i in range(1, N):
        #Lambda_i is the compensator between t(i-1) and i
        #therefore i ranges from 1 to N
        #i-1 ranges from 0 to N-1
        #when store Lambda_i into Lambda array, the first element goes to
        #index 0, so on and so forth
        storeIndex = i-1
        dur = pos[i,0] - pos[i-1,0]
        beta1 = beta[0,0]
        mu1 = mu[0,0]
        alpha11 = alpha[0,0]
        alpha12 = alpha[0,1]
        value = mu1 * dur
        part1 = alpha11/beta1 * ((1+A11[i-1,0])*(1-np.exp(-beta1*dur)))

        temp = neg[(neg>=pos[i-1,0]) & (neg<pos[i,0])]
        if temp.shape[0] > 0:
            temp = np.sum(1-np.exp(-beta1 * (pos[i,0] - temp)))
        else:
            temp = 0.0
        part2 = alpha12/beta1 * ((1-np.exp(-beta1 * dur)) * A12[i-1,0] + temp)

        value = value + part1 + part2
        Lambda1[storeIndex] = value

    for i in range(1, M):
        storeIndex = i-1
        dur = neg[i,0] - neg[i-1,0]
        beta2 = beta[1,0]
        mu2 = mu[1,0]
        alpha21 = alpha[1,0]
        alpha22 = alpha[1,1]
        value = mu2 * dur
        part1 = alpha22/beta2 * ((1+A22[i-1,0])*(1-np.exp(-beta2*dur)))

        temp = pos[(pos>=neg[i-1,0]) & (pos<neg[i,0])]
        if temp.shape[0] > 0:
            temp = np.sum(1-np.exp(-beta2 * (neg[i,0] - temp)))
        else:
            temp = 0.0
        part2 = alpha21/beta2 * ((1-np.exp(-beta2 * dur)) * A21[i-1,0] + temp)

        value = value + part1 + part2
        Lambda2[storeIndex] = value
    return Lambda1,Lambda2




def likelihood(theta,data,modelType):
    '''
    Calculate the likelihood of hawkes model given theta and data
    data is the np decomposed representation of data
    '''

    if modelType == '6':
        mu = np.array(theta[:2]).reshape(2,1)
        alpha = np.array(theta[2:6]).reshape(2,2)
    if modelType == '4':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([theta[2],theta[3],theta[3],theta[2]]).reshape(2,2)
    if modelType == '2cross':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([0.0,theta[3],theta[3],0.0]).reshape(2,2)
    #Fix beta to be [1,1,1,1]
    beta = np.ones((2,1))
    pos = data[data[:,1] == 1.0,0].reshape(-1,1)
    neg = data[data[:,1] == -1.0,0].reshape(-1,1)
    pos = pos.astype(float,copy=False)
    neg = neg.astype(float,copy=False)
    N = pos.shape[0]
    M = neg.shape[0]
    T = data[-1,0]

    R11 = getR.getR11(N,beta[0,0],pos)
    R12 = getR.getR12(N,M,beta[0,0],pos,neg)
    R21 = getR.getR21(N,M,beta[1,0],pos,neg)
    R22 = getR.getR22(M,beta[1,0],neg)

    L1 = -mu[0,0]*T -(alpha[0,0]/beta[0,0])*np.sum(1-np.exp(-beta[0,0]*(T-pos))) -\
            (alpha[0,1]/beta[0,0])*np.sum(1-np.exp(-beta[0,0]*(T-neg))) +\
            np.sum(np.log(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))

    L2 = -mu[1,0]*T -(alpha[1,0]/beta[1,0])*np.sum(1-np.exp(-beta[1,0]*(T-pos))) -\
            (alpha[1,1]/beta[1,0])*np.sum(1-np.exp(-beta[1,0]*(T-neg))) +\
            np.sum(np.log(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    return -L1-L2


def gradient(theta,data,modelType):

    if modelType == '6':
        mu = np.array(theta[:2]).reshape(2,1)
        alpha = np.array(theta[2:6]).reshape(2,2)
    if modelType == '4':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([theta[2],theta[3],theta[3],theta[2]]).reshape(2,2)
    if modelType == '2cross':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([0.0,theta[3],theta[3],0.0]).reshape(2,2)

    beta = np.ones((2,1))

    pos = data[data[:,1] == 1.0,0].reshape(-1,1)
    neg = data[data[:,1] == -1.0,0].reshape(-1,1)
    pos = pos.astype(float,copy=False)
    neg = neg.astype(float,copy=False)
    N = pos.shape[0]
    M = neg.shape[0]
    T = data[-1,0]

    R11 = getR.getR11(N,beta[0,0],pos)
    R12 = getR.getR12(N,M,beta[0,0],pos,neg)
    R21 = getR.getR21(N,M,beta[1,0],pos,neg)
    R22 = getR.getR22(M,beta[1,0],neg)

    gmu1 = -T + np.sum(1/(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))
    gmu2 = -T + np.sum(1/(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    galpha11 = -np.sum(1-np.exp(-beta[0,0]*(T-pos)))/beta[0,0] + \
            np.sum(R11[1:]/(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))

    galpha12 = -np.sum(1-np.exp(-beta[0,0]*(T-neg)))/beta[0,0] + \
            np.sum(R12[1:]/(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))

    galpha21 = -np.sum(1-np.exp(-beta[1,0]*(T-pos)))/beta[1,0] + \
            np.sum(R21[1:]/(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    galpha22 = -np.sum(1-np.exp(-beta[1,0]*(T-neg)))/beta[1,0] + \
            np.sum(R22[1:]/(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    return -np.array([gmu1,gmu2,galpha11,galpha12,galpha21,galpha22])


def learn(price,theta=(0.5,0.5,0.25,0.25,0.25,0.25),modelType = '6'):
    '''
    Learn the params using mle

    Parameters
    ----------
    price: DataFrame
        first column time and second column price

    Returns
    -------
    result: dict
        scale:  average per tick change
        params: learned value for mu and alpha
        output: all results returned by optimization function
    '''
    data,anchor = df2np(price)
    data[:,0] = np.cumsum(data[:,0])
    theta = np.array(theta)
    constraint = [(0.00001,1),(0.00001,1),(0.00001,1),(0.00001,1),(0.00001,1),(0.00001,1)]

    #learn scale
    temp  = np.diff(price.values[:,1])
    scale = np.mean(np.abs(temp[temp!=0]))
    #learn params
    args = (data,modelType)
    output = minimize(fun=likelihood,x0=theta,jac=gradient,bounds=constraint,args=args,method='L-BFGS-B')
    params = output['x']

    if modelType == '4':
        params[1] = params[0]
        params[4] = params[3]
        params[5] = params[2]
    if modelType == '2cross':
        params[1] = params[0]
        params[2] = 0.0
        params[5] = 0.0
        params[4] = params[3]

    result = {'scale':scale,'params':params,'output':output}
    return result

class hawkes:
    '''
    hawkes predictor class for learning and preditction
    '''

    def __init__(self):
        self.scale = 0
        self.modelType = '6'

    def __setparam(self,theta,scale):
        self.params = np.array(theta)
        self.scale = scale

    def fit(self,price):
        '''
        fit a hawkes model to a price sequence

        Parameters
        ----------
        price: DataFrame
            First column as time and second column as price

        Returns
        -------
        self : return a instance of self
        '''

        result =learn(price,modelType = self.modelType )
        params = result['params']
        scale = result['scale']
        self.setparam(params,scale)

    def predict(self, history, ahead = 1,density=30,mcNum = 500):
        theta = np.append(self.params,np.ones(2))
        targetTime = history.values[-1,0] + timedelta(0,ahead)
        sim = simulator(theta = theta, scale = self.scale)
        sim.sethistory(history)
        priceforecast = 0.0
        for i in range(mcNum):
            predictionSeries = sim.simulate(dataNum= (ahead*density))[0]
            predictionSeries = pd.concat([history.tail(2),predictionSeries])
            predictionSeries.index = predictionSeries['time']
            forecastIndex = predictionSeries.index.searchsorted(targetTime) - 1
            priceforecast += predictionSeries.values[forecastIndex,1]
        priceforecast /= mcNum
        output = pd.DataFrame({'time':[targetTime],'quantity':[priceforecast]},columns = ['time','quantity'])
        return output


def hawkesfeat(timeseries,params):
    '''
    Generate hawkes feature: positive rate/negtive rate
    args['params']: 1X8 ndarray containing the params of hawkes process
    '''

    #Utilize the rate calculation function in the hawkes simulator
    sim = simulator(theta = params)
    sim.sethistory(timeseries)


    rate = sim.historydata[:,2]/sim.historydata[:,3]
    rate = np.insert(rate,0,params[0]/params[1]).reshape(-1,1)
    time = np.insert(sim.historydata[:,0],0,0.0).reshape(-1,1)
    time = np.cumsum(time,axis=0)

    value = np.hstack((time,rate))
    value = value.astype(object,copy=False)
    value[:,0] = Vsecond2delta(value[:,0])

    anchor = timeseries.values[0]
    anchor[1] = 0.0
    value = value + anchor

    rateseries = pd.DataFrame(value,columns=['time','quantity'])
    rateseries.index = rateseries['time']
    rateseries = rateseries.reindex(timeseries.index,method = 'ffill')

    return rateseries

def GenerateHawkesFeature(price_, theta, seconds = 10):
    '''
    Generate a DataFrame with fields:
        time, price, pos_rate, neg_rate, rate, price_change, future_change

    Args:
        price(DataFrame):   with time and quantity fields
        theta(sequence):    1 X 8 array parameters
        seconds(float):     future_change is the price after seconds - current price

    Return:
        Feature(DataFrame): the generated feature matrix
    '''

    mu = np.array(theta[:2]).reshape(2,1)
    alpha = np.array(theta[2:6]).reshape(2,2)
    beta = np.ones((2,1))

    #mu1 = theta[0]
    #mu2 = theta[1]
    #alpha11 = theta[2]
    #alpha12 = theta[3]
    #alpha21 = theta[4]
    #alpha22 = theta[5]

    #beta1 = 1.0
    #beta2 = 1.0

    feature = price_.copy()
    feature = feature.drop_duplicates('time')
    length = feature.shape[0]
    feature['pos_rate'] = np.zeros((length,1))
    feature['neg_rate'] = np.zeros((length,1))
    feature['rate'] = np.zeros((length,1))
    feature['price_change'] = np.zeros((length,1))
    feature['future_change'] = np.zeros((length,1))

    value = feature.values

    #update price_change
    priceChange = value[1:,1] - value[:-1,1]
    priceChange = np.insert(priceChange,0,0.0)
    value[:,5] = priceChange

    #update future_change and rate
    delta = dt.timedelta(0,seconds)
    index = 0
    #futurePrice = feature[:futureTime.strftime(format = '%Y%m%d %H:%M:%S.%f')]['quantity'].irow(-1)
    #futureTime = row['time'] + delta
        #ipdb.set_trace()
                #value[index,6] = futurePrice - row['quantity']
        #ipdb.set_trace()


    for index in range(length):
        futureTime = value[index,0] + delta
        for j in range(index,length):
            if value[j,0] > futureTime:
                futurePrice = value[j-1,1]
                break
        if j == length-1:
            break

        value[index,6] = futurePrice - value[index,1]

        if index == 0:
            value[index,2:4] = mu.reshape(2)
            #value[index,2] = mu1
            #value[index,3] = mu2
        else:
            dur = (value[index,0] - value[index-1,0]).total_seconds()
            if value[index,5] > 0:
                value[index,2:4] = (mu + (value[index-1,2:4].reshape(2,1) - mu) * np.exp(-beta * dur) + alpha[:,0].reshape(2,1)).reshape(2)
            elif value[index,5] < 0:
                value[index,2:4] = (mu + (value[index-1,2:4].reshape(2,1) - mu) * np.exp(-beta * dur) + alpha[:,1].reshape(2,1)).reshape(2)
            else:
                value[index,2:4] = (mu + (value[index-1,2:4].reshape(2,1) - mu) * np.exp(-beta * dur)).reshape(2)
        index += 1

    value = value[:index,:]

    value[:,4] = value[:,2]/value[:,3]

    feature = pd.DataFrame(value,columns = ['time','price','pos_rate','neg_rate','rate','price_change','future_change'])
    return feature

