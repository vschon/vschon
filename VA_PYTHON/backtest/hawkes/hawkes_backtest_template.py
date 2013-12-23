import VA_PYTHON as va
import VD_DATABASE as vd
import ipdb

def demo():
    print 'demonstrating event system'

    sim = va.simulator.simulator.simulator()

    sim.linkTrader(va.strategy.hawkes.hawkes.hawkesTrader())

    sim.setDailyStopDelta(deltaSeconds = 300)

    parameters = {'theta':[0.5,0.5,0.1,0.5,0.5,0.1,0.6,0.6],
                  'number':100,
                  'k':3,
                  'exitdelta':20}

    sim.setTraderParams(parameters)

    sim.setData(('EURUSD',))

    sim.initializeCycle('2013.01.01','23:00:00','2013.01.03','03:00:00')

    return sim

