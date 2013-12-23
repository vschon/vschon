import VA_PYTHON as va

def demo():
    print 'demonstrating event system'

    trader = va.strategy.hawkes.hawkes.hawkesTrader()

    parameters = {'theta':[0.25,0.25,0.1,0.5,0.5,0.1, 1, 1],
                  'number':10000,
                  'k':3,
                  'exitPositionDeltaSeconds':20,
                  'stopTradingDeltaSeconds': 300}

    trader.initialize(parameters)

    trader.setData(('EURUSD', ))

    trader.initializeCycle('2013.01.01', '23:00:00', '2013.01.03', '03:00:00')

    return trader


