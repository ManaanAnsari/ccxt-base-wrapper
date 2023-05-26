import pandas as pd
from ta.trend import sma_indicator
import numpy as np
from strategies.base import Strategy



class SampleStrategy(Strategy):
    def __init__(self,symbol,exchange,exchange_params, strategy_params, df):
        # ignore last row as it is not complete yet
        df = df[:-1]
        super().__init__(symbol,exchange,exchange_params, strategy_params, df, "SampleStrategy")
    

    def calculateSignals(self):
        self.df['sma_10'] = sma_indicator(self.df['close'],window=10,fillna=True)
        self.df['sma_20'] = sma_indicator(self.df['close'],window=20,fillna=True)



    def takeSignalAction(self):
        row = self.df.iloc[-1]
        if row["sma_10"] > row["sma_20"]:
            # check if not in long position
            if self.isInPosition("short"):
                self.closeAllPositions("short")
                
            if not self.isInPosition("long"):
                print("go long")
                tp_price= float(row["close"]) - float(row["close"]) *self.strategy_params.get("sl_perc", 0.03)
                sl_price= float(row["close"]) + float(row["close"]) * self.strategy_params.get("tp_perc", 0.03)
                qty = self.getQty()
                self.goLong(qty=qty,tp_price=tp_price,sl_price=sl_price)

        else:
            if self.isInPosition("long"):
                self.closeAllPositions("long")
            
            if not self.isInPosition("short"):
                print("go short")
                tp_price= float(row["close"]) - float(row["close"]) *self.strategy_params.get("sl_perc", 0.03)
                sl_price= float(row["close"]) + float(row["close"]) * self.strategy_params.get("tp_perc", 0.03)
                qty = self.getQty()
                self.goShort(qty=qty,tp_price=tp_price,sl_price=sl_price)
    
