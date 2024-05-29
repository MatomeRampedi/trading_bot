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

# Function to place a buy order
def place_buy_order(symbol, lot, price, sl, tp):
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print("Failed to get symbol info for", symbol)
        return None

    print(f"Symbol info for {symbol}:")
    print(f"  Volume Min: {symbol_info.volume_min}")
    print(f"  Volume Max: {symbol_info.volume_max}")
    print(f"  Volume Step: {symbol_info.volume_step}")

    # Adjust volume to be within allowed range and a multiple of volume_step
    volume_min = symbol_info.volume_min
    volume_max = symbol_info.volume_max
    volume_step = symbol_info.volume_step

    if lot < volume_min:
        lot = volume_min
    elif lot > volume_max:
        lot = volume_max
    else:
        lot = round(lot / volume_step) * volume_step

    # Check if the adjusted volume is valid
    if lot < volume_min or lot > volume_max or lot % volume_step != 0:
        print(f"Adjusted volume {lot} is invalid")
        return None

    print(f"Adjusted lot size: {lot}")

    point = symbol_info.point
    deviation = 10
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - sl * point,
        "tp": price + tp * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": "Python script order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    print("Order request:")
    print(request)

    result = mt5.order_send(request)
    return result

# Example usage
symbol = "EURUSD"
lot = 0.01  # Adjust this value as needed
sl = 100  # Stop loss in points
tp = 100  # Take profit in points

# Get market data
data = get_market_data(symbol, mt5.TIMEFRAME_M1, 10)
print(data)

# Place a buy order
price = mt5.symbol_info_tick(symbol).ask
result = place_buy_order(symbol, lot, price, sl, tp)

# Check the result of the order
if result is None:
    print("Order failed due to invalid volume")
elif result.retcode != mt5.TRADE_RETCODE_DONE:
    print("Order failed, retcode =", result.retcode)
    print("Detailed order result:")
    print(result)
else:
    print("Order placed successfully, order ticket number =", result.order)

# Shutdown connection to MT5
mt5.shutdown()