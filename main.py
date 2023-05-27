import ccxt
import pandas as pd
import schedule
import time
import config as conf
from strategies.SampleStrategy import SampleStrategy
from config import run_data



exchange = ccxt.binance(
    {
        "enableRateLimit": True,
        'options': {
            'defaultType': 'future',
        },
    }
)


def fetchCandle(symbol, timeframe, ongoing=True):
    print("fetching candle..."+symbol+" "+timeframe)
    response = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=1000)
    # remove ongoing candle
    if ongoing:
        df = pd.DataFrame(response, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    else:
        df = pd.DataFrame(response[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df



def runStrategy():
    print("running strategy...")
    # 4h
    for tf, symbol_dict in run_data.items():
        # btc/usdt
        for symbol, strategy_dict in symbol_dict.items():
            df = fetchCandle(symbol,tf)
            # pivotstandard
            for strategy, strategy_data in strategy_dict.items():       
                # custom
                for user_exchange in strategy_data["custom"]:
                    try:
                        # rerun with custom strat params
                        strat_param = user_exchange["strategy_params"]
                        print(user_exchange["exchange"])
                        print("running strategy: "+strategy+" on "+symbol+" with "+tf+" timeframe")
                        print("custom strategy params: "+str(strat_param)+" and exchange params: "+str(user_exchange["exchange_params"]))
                        
                        strat = SampleStrategy(symbol,user_exchange['exchange'],user_exchange["exchange_params"],strat_param,df.copy())
                        strat.calculateSignals()
                        strat.takeSignalAction()
                        
                    except Exception as e:
                        print("Error in user exchange",e)
                        conf.logging.error("Error in user exchange")

                        if user_exchange.get("exchange_params",None):
                            if user_exchange.get("exchange_params",None).get("API_KEY",None):
                                user_exchange["exchange_params"]["API_KEY"] = "***"
                            if user_exchange.get("exchange_params",None).get("API_KEY_SECRET",None):
                                user_exchange["exchange_params"]["API_KEY_SECRET"] = "***"
                            if user_exchange.get("exchange_params",None).get("PASSWORD",None):
                                user_exchange["exchange_params"]["PASSWORD"] = "***"

                        conf.logging.error(str(user_exchange))
                        conf.logging.error(e)
                        continue



def keepRunning():
    try:
        runStrategy()
    except Exception as e:
        print("Error in running strategy",e)
        conf.logging.error("Error in running strategy")
        conf.logging.error(e)
        

schedule.every(30).seconds.do(keepRunning)

while True:
    schedule.run_pending()
    time.sleep(1)
