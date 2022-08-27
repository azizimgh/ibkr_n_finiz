
from matplotlib.pyplot import bar
import config
from ib_insync import *


def get_klines_data(list_symbol=[]):
    ib = IB()
    ib.connect('127.0.0.1', config.tws_port, clientId=1)
    if config.allow_delayed_data:
        ib.reqMarketDataType(4)

    try:
        to_return = {}
        for symbol in list_symbol:
            stock = Stock(
                         symbol, 
                        'SMART', 
                        'USD'
                            )

            bars = ib.reqHistoricalData(
                        stock,
                        endDateTime='',
                        durationStr=str(config.ipo_check)+' D',
                        barSizeSetting='1 day',
                        whatToShow='TRADES',
                        useRTH=True,
                        formatDate=1)
            
            total_days = len(bars)
 
            if total_days >= config.ipo_check: # respects Ipo minimum days
                ipo = True
                open_today = bars[-1].open
                volume_yesterday = bars[-2].volume
                low_yesterday = bars[-2].low
                low_day_before = bars[-3].low

            else:
                ipo = False
                open_today = 0
                volume_yesterday = 0
                low_yesterday = 0
                low_day_before = 0
            
            temp_data = {"ipo":ipo,
                    "open_today":open_today,
                    "volume_yesterday":volume_yesterday,
                    "low_yesterday":low_yesterday,
                    "low_day_before":low_day_before}

            to_return[symbol]=temp_data
        return to_return

    except Exception as e:
        print(e)

    finally:
        ib.disconnect()



def get_top_volume_stocks():
    ib = IB()
    ib.connect('127.0.0.1', config.tws_port, clientId=2)
    if config.allow_delayed_data:
        ib.reqMarketDataType(4)

    try:

        hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                    locationCode='STK.US.MAJOR',
                                    scanCode='HOT_BY_VOLUME')

        scanner = ib.reqScannerData(hot_stk_by_volume, [])
        
        return [stock.contractDetails.contract.symbol for stock in scanner]
    
    except Exception as e:
        print(e)
        return []

