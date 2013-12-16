import VA_PYTHON as va
import VD_KDB as vd
import ipdb

def demo():
    print 'demonstrating event system'

    #1. create simulator
    sim = va.simulator.simulator.simulator()

    ####Initialization####

    #2. set data list
    sim.setdatalist(('forex_quote-usdjpy',))

    #3. set market list
    #set the first 2 element in datalist as market list
    sim.setMarketList(1)

    #4. set order matcher for each market data
    sim.setOrderMatcher(['forex_quote',])

    #5. set delay time for each order matcher
    sim.setDelayTime((2000,))

    #6. match trade symbol and market data index
    sim.matchSymbol(['usdjpy-0',])

    #7. set cycles
    sim.setCycle('2013.01.01','23:00:00','2013.03.31','07:00:00')
    ####CHECK CYCLE AND REPLACE DATA

    #8. set daily stop time delta(in seconds)
    sim.setDailyStopDelta(300)

    #9. set sim timer increment (in microseconds)
    sim.setSimTimerIncrement(1000)


    parameters = {'theta':[0.5,0.5,0.1,0.5,0.5,0.1,0.6,0.6],
                  'number':100,
                  'k':2,
                  'exitdelta':20}

    sim.setTraderParams(parameters)

    #9. config portfolio
    sim.setcapital(1000000.0)

    #10. set trader
    #sim.setTrader('hawkes')
    sim.trader = va.strategy.hawkes.hawkes.hawkesTrader_filter()

    #10.1 set trader name
    sim.trader.setname('hawkes_filter')

    #10.2 set symbol list
    #the index of each symbol corresponds to the symbol index used by the trader
    sim.trader.setsymbols(['usdjpy',])

    #set trader sender for each symbol
    sim.trader.setsender([sim.simOrderProcessor,])

    #set filter for each market
    sim.trader.setfilter(['forex_quote-single_price',])

    #set trader reverse flag
    sim.trader.Reverse(False)

    return sim

