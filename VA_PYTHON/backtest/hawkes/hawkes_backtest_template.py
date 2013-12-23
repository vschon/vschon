import VA_PYTHON as va
import VD_DATABASE as vd
import ipdb

def demo():
    print 'demonstrating event system'

    #1. create simulator
    sim = va.simulator.simulator.simulator()

    #####################
    #Trader configuration
    #####################
    #2. link trader and simulator
    sim.linkTrader(va.strategy.hawkes.hawkes.hawkesTrader())

    #3. set the time delta to stop entering new trades in advance
    sim.setDailyStopDelta(deltaSeconds = 300)

    #4. set parameters
    parameters = {'theta':[0.5,0.5,0.1,0.5,0.5,0.1,0.6,0.6],
                  'number':100,
                  'k':3,
                  'exitdelta':20}

    sim.setTraderParams(parameters)

    ####################
    # Data configuration
    ####################

    #2. set dataCells
    #dataCells used for matching orders are put first
    #sim.initializeDataCells(('forex_quote-EURUSD', ))
    sim.setData(('EURUSD',))


    ###################
    #Time configuration
    ###################
    #8. initialze cyclemanager
    sim.initializeCycle('2013.01.01','23:00:00','2013.01.03','03:00:00')

    return sim

