import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time

# Connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Log in to a trading account
account = 5024763850
password = "E-D5FoMb"
server = "MetaQuotes-Demo"

authorized = mt5.login(account, password, server)
if not authorized:
    print("Failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
    quit()

print("Connected to account #{}".format(account))

def get_market_data(symbol, timeframe, num_bars):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    if rates is None:
        print("Failed to get market data, error code =", mt5.last_error())
        quit()
    data_frame = pd.DataFrame(rates)
    data_frame['time'] = pd.to_datetime(data_frame['time'], unit='s')
    return data_frame

def engulfing_pattern_strategy(df):
    engulfing_patterns = []

    # for i in range(1, len(df)):
        # Previous and current candles
    open = df['open'].iloc[-1]
    close = df['close'].iloc[-2]
    previous_open = df['open'].iloc[-3]
    previous_close = df['close'].iloc[-3]

     # Bearish Pattern
    if (open>close and 
    previous_open<previous_close and 
    close<previous_open and
    open>=previous_close):
        return 1

    # Bullish Pattern
    elif (open<close and 
        previous_open>previous_close and 
        close>previous_open and
        open<=previous_close):
        return 2
    
    # No clear pattern
    else:
        return 0
# Function to place a buy order
def place_order(symbol, lot, price, order_type):
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print("Failed to get symbol info for", symbol)
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "position": mt5.positions_get()[0].asdict()['ticket'],
        "price": price,
        "comment": "Python script close position",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    return result

def close_order(symbol, lot, price, order_type, sl, tp):
    symbol_info = mt5.symbol_info(symbol)
    point = symbol_info.point
    deviation = 10
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl * point,
        "tp": tp * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": "Python script open position",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    return result

# Example usage
symbol = "USDZAR"
lot = 0.05  # Adjust this value as needed
sl = 50  # Stop loss in points
tp = 100  # Take profit in points

# "sl": price - sl * point,
# "tp": price + tp * point,

buy_price = mt5.symbol_info_tick(symbol).ask
sell_price = mt5.symbol_info_tick(symbol).bid
sl_perc = 0.05
tp_perc = 0.1
buy_sl = buy_price - sl 
buy_tp = buy_price + tp
sell_sl =  sell_price + sl
sell_tp = sell_price - tp
# Get market data
while True:
    data = get_market_data(symbol, mt5.TIMEFRAME_M1, 10)

    signal = engulfing_pattern_strategy(data)
    if signal > 0:
        break
print(signal)
try:
    check_sell = mt5.positions_get()[0]._asdict()['type'] == 1
    check_buy = mt5.positions_get()[0]._asdict()['type'] == 0
except:
    pass
# Place a buy order
if signal == 1:
    # sell
   result = place_order(symbol, lot, sell_price, mt5.ORDER_TYPE_SELL)
   print("Sell : ", result)
elif signal == 2:
    # buy
    result = place_order(symbol, lot, buy_price, mt5.ORDER_TYPE_BUY)
    print("Buy : ", result)

else:
    pass
    print(None)


# Check the result of the order
# if result is None:
#     print("Order failed due to invalid volume")
# elif result.retcode != mt5.TRADE_RETCODE_DONE:
#     print("Order failed, retcode)
#     print("Detailed order result:")
#     print(result)
# else:
#     print("Order placed successfully, order ticket number =", result.order)

# Shutdown connection to MT5
mt5.shutdown()