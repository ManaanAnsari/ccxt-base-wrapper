import ccxt
from config import logging
from notification import send_telegram_message
import time


class Strategy:
    def __init__(self,symbol,exchange,exchange_params, strategy_params, df,name):
        self.strategy_name = name
        self.exchange_params = exchange_params
        self.exchange_name = exchange
        self.strategy_params = strategy_params if strategy_params else {}
        self.leverage = 1
        self.symbol= symbol
        self.temp_symbol= symbol
        self.df = df
        
        if exchange == "binance":
            self.exchange = ccxt.binance(
                {
                    "apiKey": exchange_params["API_KEY"],
                    "secret": exchange_params["API_KEY_SECRET"],
                    "enableRateLimit": True,
                    'options': {
                        'defaultType': 'future',
                    },
                }
            )
            if exchange_params["TESTNET"]:
                print("using testnet")
                self.exchange.set_sandbox_mode(True)
        elif exchange == "kucoin":
            self.exchange = ccxt.kucoinfutures(
                {
                    "apiKey": exchange_params["API_KEY"],
                    "secret": exchange_params["API_KEY_SECRET"],
                    "password": exchange_params["PASSWORD"],
                    "enableRateLimit": True,
                
                }
            )
            self.temp_symbol = symbol+":"+symbol.split("/")[1]
            if exchange_params["TESTNET"]:
                print("using testnet")
                self.exchange.set_sandbox_mode(True)
        elif exchange == "bitmex":
            self.exchange = ccxt.bitmex({
                "apiKey": exchange_params["API_KEY"],
                "secret": exchange_params["API_KEY_SECRET"],
                "enableRateLimit": True,
                'options': {
                    'defaultType': 'future',
                },
            })
            
            self.temp_symbol = symbol.replace("/","")
            self.temp_symbol = self.temp_symbol.replace("BTC","XBT")
            if exchange_params["TESTNET"]:
                print("using testnet")
                self.exchange.set_sandbox_mode(True)

        else:
            raise Exception("Exchange not supported")
        self.setLeverage()
        
        
    def setLeverage(self):
        if self.exchange_name == "binance":
            try:
                self.exchange.set_margin_mode(symbol=self.temp_symbol,marginMode= "isolated",params={"type": "future"})
            except Exception as e:
                print(e)
                logging.error(e)
                
            try:
                self.exchange.set_leverage(symbol=self.temp_symbol, leverage= self.strategy_params["leverage"],params={"type": "future"})
            except Exception as e:
                print(e)
                logging.error(e)
        
        if self.exchange_name == "bitmex":
            try:
                self.exchange.set_margin_mode(symbol=self.temp_symbol,marginMode= "isolated",params={"type": "future"})
            except Exception as e:
                print(e)
                logging.error(e)
                
            try:
                self.exchange.set_leverage(symbol=self.temp_symbol, leverage= self.strategy_params["leverage"],params={"type": "future"})
            except Exception as e:
                print(e)
                logging.error(e)
            
        self.leverage = self.strategy_params["leverage"]
            

    def sendNotification(self,msgs):
        if self.exchange_params.get("telegram_chat_id",None) and len(msgs):
            msgs = [f"{self.exchange_name}-{self.strategy_name}: "+str(msg) for msg in msgs]
            send_telegram_message(chat_ids=[self.exchange_params.get("telegram_chat_id",None)],messages=msgs)

    
    def changeUserExchange(self,exchange,exchange_params):
        self.exchange_params = exchange_params
        if exchange == "binance":
            self.exchange = ccxt.binance(
                {
                    "apiKey": exchange_params["API_KEY"],
                    "secret": exchange_params["API_KEY_SECRET"],
                    "enableRateLimit": True,
                    # 'options': {
                    #     'defaultType': 'future',
                    # },
                }
            )
            self.exchange.options['defaultType'] = 'future'
            if exchange_params["TESTNET"]:
                self.exchange.set_sandbox_mode(True)
        else:
            raise Exception("Exchange not supported")
        
    
    def getBalance(self,token_symbol):
        print("fetching balance..."+token_symbol)
        bal = self.exchange.fetch_balance({"type": "future","marginType": "isolated"})
        return float(bal["free"].get(token_symbol,0))

    def getRiskableBalance(self,token_symbol):
        return round(self.getBalance(token_symbol) * self.strategy_params["risk_perc"],2)

    def getTime(self):
        
        t = str(int(time.time() * 1000))
        print(t)
        return t

    def closeAllOpenOrders(self,ptype):
        buysell = "sell" if ptype == "long" else "buy"
        if self.exchange_name == "binance":
            op = self.exchange.fetch_open_orders(self.temp_symbol)
            for open_order in op:
                if open_order["side"] == buysell and open_order["type"] in ["stop_market","take_profit_market"] :
                    order = self.exchange.cancel_order(open_order["id"], open_order["symbol"])
                    print(order)
                    logging.info("cancel order "+self.temp_symbol+" order id: "+str(open_order["id"])+" type: "+open_order["type"]+" side: "+open_order["side"]+"")
        elif self.exchange_name == "kucoin":
            op = self.exchange.fetch_open_orders(self.temp_symbol,params={"stop":True})
            for open_order in op:
                if open_order["side"] == buysell:
                    order = self.exchange.cancel_order(open_order["id"], open_order["symbol"])
                    print(order)
                    logging.info("cancel order "+self.temp_symbol+" order id: "+str(open_order["id"])+" type: "+open_order["type"]+" side: "+open_order["side"]+"")
        elif self.exchange_name == "bitmex":
            op = self.exchange.fetch_open_orders(self.temp_symbol)
            for open_order in op:
                if open_order["side"] == buysell and open_order["type"] in ["stop","marketiftouched"]:
                    order = self.exchange.cancel_order(open_order["id"], open_order["symbol"])
                    print(order)
                    logging.info("cancel order "+self.temp_symbol+" order id: "+str(open_order["id"])+" type: "+open_order["type"]+" side: "+open_order["side"]+"")


    def closeAllPositions(self,ptype):
        buysell = "sell" if ptype == "long" else "buy"
        telemsg = []
        if self.exchange_name == "binance":
            positions = self.exchange.fetch_positions(symbols=[self.temp_symbol])
            for pos in positions:
                if pos["side"] == ptype:
                    if pos["info"].get("positionAmt",None):
                        qty = float(pos["info"].get("positionAmt",None))
                        if qty < 0:
                            qty = -1*qty
                        try:
                            order = self.exchange.create_order(self.temp_symbol, 'market', buysell, qty,{"reduceOnly": True})
                            print(order)
                            msg="close position "+self.temp_symbol+" order id: "+str(order["id"])+" type: "+str(order["type"])+" side: "+str(order["side"])+""
                            logging.info(msg)
                            telemsg.append(msg)
                        except Exception as e:
                            print(e)
                            logging.info("error while closing position")
                            logging.error(e)
                            telemsg.append("error while closing position")
                            
        elif self.exchange_name == "kucoin":
            positions = self.exchange.fetch_positions(symbols=[self.temp_symbol])
            for pos in positions:
                if pos["side"] == ptype:
                    if pos["info"].get("currentQty",None):
                        qty = float(pos["info"].get("currentQty",None))
                        if qty < 0:
                            qty = -1*qty
                        try:
                            order = self.exchange.create_order(self.temp_symbol, 'market', buysell, qty,{"reduceOnly": True})
                            print(order)
                            msg="close position "+self.temp_symbol+" order id: "+str(order["id"])+" type: "+str(order["type"])+" side: "+str(order["side"])+""
                            logging.info(msg)
                            telemsg.append(msg)
                        except Exception as e:
                            print(e)
                            logging.info("error while closing position")
                            logging.error(e)
                            telemsg.append("error while closing position")
                            
        elif self.exchange_name == "bitmex":
            positions = self.exchange.fetch_positions(symbols=[self.temp_symbol])
            for pos in positions:
                if pos["info"].get("currentQty",None):
                    qty = float(pos["info"].get("currentQty",0))
                    try:
                        if qty and qty < 0 and ptype == "short":
                            qty = -1*qty
                            order = self.exchange.create_order(self.temp_symbol, 'market', buysell, qty,None,{"reduceOnly": True})
                            print(order)
                            msg="close position "+self.temp_symbol+" order id: "+str(order["id"])+" type: "+str(order["type"])+" side: "+str(order["side"])+""
                            logging.info(msg)
                            telemsg.append(msg)
                        elif qty and qty > 0 and ptype == "long":
                            order = self.exchange.create_order(self.temp_symbol, 'market', buysell, qty,None,{"reduceOnly": True})
                            print(order)
                            msg="close position "+self.temp_symbol+" order id: "+str(order["id"])+" type: "+str(order["type"])+" side: "+str(order["side"])+""
                            logging.info(msg)
                            telemsg.append(msg)
                    except Exception as e:
                        print(e)
                        logging.info("error while closing position")
                        logging.error(e)
                        telemsg.append("error while closing position")
            
        self.sendNotification(telemsg)
        self.closeAllOpenOrders(ptype)


    def isInPosition(self,ptype):
        if self.exchange_name == "binance":
            positions = self.exchange.fetch_positions(symbols=[self.temp_symbol])
            for pos in positions:
                if pos["side"] == ptype:
                    if pos["info"].get("positionAmt",None):
                        qty = float(pos["info"].get("positionAmt",None))
                        if qty:
                            return True
        elif self.exchange_name == "kucoin":
            positions = self.exchange.fetch_positions(symbols=[self.temp_symbol])
            for pos in positions:
                if pos["side"] == ptype:
                    if pos["info"].get("currentQty",None):
                        qty = float(pos["info"].get("currentQty",None))
                        if qty:
                            return True
        elif self.exchange_name == "bitmex":
            positions = self.exchange.fetch_positions(symbols=[self.temp_symbol])
            for pos in positions:
                if pos.get("info",{}).get("currentQty",0):
                    qty = float(pos.get("info",{}).get("currentQty",0))
                    if qty and qty < 0 and ptype == "short":
                        return True
                    elif qty and qty > 0 and ptype == "long":
                        return True
                    else:
                        return False
        return False

    def getQty(self):
        bal = self.getRiskableBalance(self.symbol.split("/")[1])
        qty = (bal*self.leverage)/self.df.iloc[-1]["close"]
        if self.exchange_name == "binance":
            qty = self.exchange.amount_to_precision(self.temp_symbol, qty)
        elif self.exchange_name == "kucoin":
            qty = qty*1000
            print(qty)
            if qty>1:
                qty = self.exchange.amount_to_precision(self.temp_symbol, qty)
            else:
                qty = 0
        elif self.exchange_name == "bitmex":
            try:
                market = self.exchange.market(self.temp_symbol)
                qty = int(qty *float(market["info"]["underlyingToPositionMultiplier"]))
                print(qty)
            except Exception as e:
                print(e)
                qty = 0
            if qty>1:
                qty = self.exchange.amount_to_precision(self.temp_symbol, qty)
            else:
                qty = 0
        return float(qty)
    
    def tpslCheck(self,ptype:str,priv_close:float,tp_price:float=None,sl_price:float=None):
        perc = float(self.strategy_params.get("tpsl_buffer_perc",0)) if self.strategy_params.get("tpsl_buffer_perc",None) else 0.05
        tp,sl = tp_price, sl_price
        telemsg = []
        if ptype == "long":
            if tp_price:
                # should be atlest 3% above priv_close 
                tp_target = priv_close + (priv_close*perc)
                if tp_price < tp_target:
                    tp= round(tp_target,2) 
                    telemsg.append(self.temp_symbol+": "+ptype+" take profit price is too close to the closing price "+str(priv_close) +" changed it to "+str(tp)+" from "+str(tp_price)+"")
                    
            if sl_price:
                # should be atlest 3% below priv_close
                sl_target = priv_close - (priv_close*perc)
                if sl_price > sl_target:
                    sl= round(sl_target,2)
                    telemsg.append(self.temp_symbol+": "+ptype+" stop loss price is too close to the closing price "+str(priv_close) +" changed it to "+str(sl)+" from "+str(sl_price)+"")
                
        elif ptype == "short":
            if tp_price:
                # should be atlest 3% below priv_close
                tp_target = priv_close - (priv_close*perc)
                if tp_price > tp_target:
                    tp= round(tp_target,2)
                    telemsg.append(self.temp_symbol+": "+ptype+" take profit price is too close to the closing price "+str(priv_close) +" changed it to "+str(tp)+" from "+str(tp_price)+"")
            if sl_price:
                # should be atlest 3% above priv_close
                sl_target = priv_close + (priv_close*perc)
                if sl_price < sl_target:
                    sl= round(sl_target,2)
                    telemsg.append(self.temp_symbol+": "+ptype+" stop loss price is too close to the closing price "+str(priv_close) +" changed it to "+str(sl)+" from "+str(sl_price)+"")
        
        self.sendNotification(telemsg)
        return tp,sl

    def goLong(self,qty,tp_price=None,sl_price=None):
        print("enter long position "+self.temp_symbol+" qty: "+str(qty))
        close = float(self.df.iloc[-1]["close"])
        # enter long position
        long,tp,sl = None,None,None
        telemsg = []
        skip_all = False
        tp_price,sl_price = self.tpslCheck("long",close,tp_price,sl_price)
        try:
            msg = ""
            if self.exchange_name == "binance":
                long = self.exchange.create_order(self.temp_symbol, 'market', 'buy', qty)
                msg = "enter long position "+self.temp_symbol+" at: "+str(close)+" qty: "+str(qty)+" order id: "+str(long["id"])+" "
            elif self.exchange_name == "kucoin":
                long = self.exchange.create_order(self.temp_symbol, 'market', 'buy', qty, None, {"marginMode":"isolated","leverage":self.leverage})
                msg = "enter long position "+self.temp_symbol+" at: "+str(close)+" qty: "+str(qty)+" order id: "+str(long["id"])+" "
            elif self.exchange_name == "bitmex":
                long = self.exchange.create_order(self.temp_symbol, 'market', 'buy', qty, None, {"leverage":self.leverage})
                msg = "enter long position "+self.temp_symbol+" at: "+str(close)+" qty: "+str(qty)+" order id: "+str(long["id"])+" "
            
            if msg:
                logging.info(msg)
                telemsg.append(msg)
                
        except Exception as e:
            print(e)
            msg = "error in creating long order for "+self.temp_symbol+" qty: "+str(qty)
            logging.error(msg)
            logging.error(e)
            telemsg.append(msg)
            skip_all = True
            
        if long is not None:
            if tp_price and not skip_all:
                tp_price = round(tp_price,2)
                try:
                    msg = ""
                    if self.exchange_name == "binance":
                        tp = self.exchange.create_order(self.temp_symbol, 'TAKE_PROFIT_MARKET', 'sell', qty, None, {"stopPrice": tp_price,"reduceOnly": True})
                        msg = "enter long tp order "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)+" order id: "+str(tp["id"])+" "
                    elif self.exchange_name == "kucoin":
                        tp = self.exchange.create_order(self.temp_symbol, 'market', 'sell', qty, None, {"stopPrice": tp_price,"stop":"up","reduceOnly":True})
                        msg = "enter long tp order "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)+" order id: "+str(tp["id"])+" "
                    elif self.exchange_name == "bitmex":
                        tp = self.exchange.create_order(
                            symbol=self.temp_symbol,
                            type='MarketIfTouched',
                            side='sell',
                            amount=qty,
                            price=tp_price,
                            params={
                                'stopPx': tp_price,
                                'execInst': 'ReduceOnly'
                            }
                        )
                        msg = "enter long tp order "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)+" order id: "+str(tp["id"])+" "

                    if msg:
                        logging.info(msg)
                        telemsg.append(msg)
                except Exception as e:
                    print(e)
                    msg = "error in creating long tp order for "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)
                    logging.error(msg)
                    logging.error(e)
                    telemsg.append(msg)
                    skip_all = True
                    
            if sl_price and not skip_all:
                sl_price = round(sl_price,2)
                try:
                    msg=""
                    if self.exchange_name == "binance":
                        sl = self.exchange.create_order(self.temp_symbol, 'STOP_MARKET', 'sell', qty, None, {"stopPrice": sl_price,"reduceOnly": True})
                        msg = "enter long sl order "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)+" order id: "+str(sl["id"])+" "
                    if self.exchange_name == "kucoin":
                        sl = self.exchange.create_order(self.temp_symbol, 'market', 'sell', qty, None, {"stopPrice": sl_price,"stop":"down","reduceOnly": True})
                        msg = "enter long sl order "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)+" order id: "+str(sl["id"])+" "
                    if self.exchange_name == "bitmex":
                        sl = self.exchange.create_order(
                            symbol=self.temp_symbol,
                            type='stop',
                            side='sell',
                            amount=qty,
                            price=sl_price,
                            params={
                                'stopPx': sl_price,
                                'execInst': 'ReduceOnly'
                            }
                        )
                        msg = "enter long sl order "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)+" order id: "+str(sl["id"])+" "
                                            
                    if msg:
                        logging.info(msg)
                        telemsg.append(msg)
                except Exception as e:
                    msg = "error in creating long sl order for "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)
                    print(e)
                    logging.error(msg)
                    logging.error(e)
                    telemsg.append(msg)
                    skip_all = True
        
        if skip_all:
            telemsg.append("to keep funds safe canceling/closing all long orders for "+self.temp_symbol+" : tp/sl error might have occured")
        self.sendNotification(telemsg)
        if skip_all:
            self.closeAllPositions("long")
        print(long,tp,sl)
        return long,tp,sl

    
    def goShort(self,qty,tp_price=None,sl_price=None):
        close = float(self.df.iloc[-1]["close"])
        # todo: add qty check min max + liq price
        print("enter short position"+self.temp_symbol+" qty: "+str(qty))
        # enter short position
        short,tp,sl = None,None,None
        telemsg = []
        skip_all = False
        tp_price,sl_price = self.tpslCheck("short",close,tp_price,sl_price)
        try:
            msg = ""
            if self.exchange_name == "binance":
                short = self.exchange.create_order(self.temp_symbol, 'market', 'sell', qty)
                msg = "enter short position "+self.temp_symbol+" at:"+str(close)+" qty: "+str(qty)+" order id: "+str(short["id"])+" "
            elif self.exchange_name == "kucoin":
                short = self.exchange.create_order(self.temp_symbol, 'market', 'sell', qty, None, {"marginMode":"isolated","leverage":self.leverage})
                msg = "enter short position "+self.temp_symbol+" at:"+str(close)+" qty: "+str(qty)+" order id: "+str(short["id"])+" "
            
            elif self.exchange_name == "bitmex":
                short = self.exchange.create_order(
                    self.temp_symbol, 
                    type='market', 
                    side='sell', 
                    amount=qty, 
                    price=None,
                    params={"leverage":self.leverage}
                )
                msg = "enter short position "+self.temp_symbol+" at:"+str(close)+" qty: "+str(qty)+" order id: "+str(short["id"])+" "
            
            if msg:
                logging.info(msg)
                telemsg.append(msg)
        except Exception as e:
            msg = "error in creating short order for "+self.temp_symbol+" qty: "+str(qty)
            print(e)
            logging.error(msg)
            logging.error(e)
            telemsg.append(msg)
            skip_all = True
        
        if short is not None:
            if tp_price and not skip_all:
                tp_price = round(tp_price,2)
                try:
                    msg = ""
                    if self.exchange_name == "binance":
                        # tp = row["support_1"] or row["support_2"]
                        tp = self.exchange.create_order(self.temp_symbol, 'TAKE_PROFIT_MARKET', 'buy', qty, None, {"stopPrice": tp_price,"reduceOnly": True})
                        msg = "enter short tp order "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)+" order id: "+str(tp["id"])+" "
                    elif self.exchange_name == "kucoin":
                        tp = self.exchange.create_order(self.temp_symbol, 'market', 'buy', qty, None, {"stopPrice": tp_price,"stop":"down","reduceOnly":True})
                        msg = "enter short tp order "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)+" order id: "+str(tp["id"])+" "
                    
                    elif self.exchange_name == "bitmex":
                        tp = self.exchange.create_order(
                            symbol=self.temp_symbol,
                            type='MarketIfTouched',
                            side='buy',
                            amount=qty,
                            price=tp_price,
                            params={
                                'stopPx': tp_price,
                                'execInst': 'ReduceOnly'
                            }
                        )
                        msg = "enter short tp order "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)+" order id: "+str(tp["id"])+" "
                    
                    if msg:
                        logging.info(msg)
                        telemsg.append(msg)
                except Exception as e:
                    msg = "error in creating short tp order for "+self.temp_symbol+" qty: "+str(qty)+" tp_price: "+str(tp_price)
                    print(e)
                    logging.error(msg)
                    logging.error(e)
                    telemsg.append(msg)
                    skip_all = True
            
            if sl_price and not skip_all:
                sl_price = round(sl_price,2)
                try:
                    msg = ""
                    if self.exchange_name == "binance":
                        # sl = row["pivot_point"] or row["resistance_1"] or row["resistance_2"]
                        sl = self.exchange.create_order(self.temp_symbol, 'STOP_MARKET', 'buy', qty, None, {"stopPrice": sl_price,"reduceOnly": True})
                        msg = "enter short sl order "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)+" order id: "+str(sl["id"])+" "
                    elif self.exchange_name == "kucoin":
                        sl = self.exchange.create_order(self.temp_symbol, 'market', 'buy', qty, None, {"stopPrice": sl_price,"stop":"up","reduceOnly": True})
                        msg = "enter short sl order "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)+" order id: "+str(sl["id"])+" "
                    elif self.exchange_name == "bitmex":
                        sl = self.exchange.create_order(
                            symbol=self.temp_symbol,
                            type='stop',
                            side='buy',
                            amount=qty,
                            price=sl_price,
                            params={
                                'stopPx': sl_price,
                                'execInst': 'ReduceOnly'
                            }
                        )
                        msg = "enter short sl order "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)+" order id: "+str(sl["id"])+" "
                    
                    if msg:
                        logging.info(msg)
                        telemsg.append(msg)
                except Exception as e:
                    msg = "error in creating short sl order for "+self.temp_symbol+" qty: "+str(qty)+" sl_price: "+str(sl_price)
                    print(e)
                    logging.error(msg)
                    logging.error(e)
                    telemsg.append(msg)
                    skip_all = True
        
        if skip_all:
            telemsg.append("to keep funds safe canceling/closing all short orders for "+self.temp_symbol+" : tp/sl error might have occured")
        self.sendNotification(telemsg)
        if skip_all:
            self.closeAllPositions("short")
        print(short,tp,sl)
        return short,tp,sl