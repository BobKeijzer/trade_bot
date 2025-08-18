import ccxt
import pandas as pd
import ta
import pytz
from datetime import datetime

# Set up exchange
exchange = ccxt.mexc({
    'apiKey': "your_api_key_here",
    'secret': "your_api_secret_here",
})
timezone = pytz.timezone('Europe/Amsterdam')

# Strategy Configuration
symbol = 'BTC/USDC'
order_buffer_pct = 0.9  # Use 90% of available balance to avoid errors

def fetch_ohlcv(symbol, timeframe, limit):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df.tz_localize(pytz.utc).tz_convert(timezone)
        return df
    except Exception as e:
        print(f"Error fetching OHLCV data: {e}")
        return None

def calculate_indicators(df, macd_params):
    macd = ta.trend.MACD(df['close'], window_slow=macd_params['slow'], window_fast=macd_params['fast'], window_sign=macd_params['signal'])
    df['macd_diff'] = macd.macd_diff()
    df['macd_signal'] = macd.macd_signal()
    return df

def place_order(order_type, amount):
    try:
        if order_type == 'buy':
            exchange.create_market_buy_order(symbol, amount)
        elif order_type == 'sell':
            exchange.create_market_sell_order(symbol, amount)
        return True
    except Exception as e:
        print(f"Error placing {order_type} order: {e}")
        return False

def check_conditions_and_trade():
    try:
        # Fetch data for the timeframes
        df_diff = fetch_ohlcv(symbol, '1h', 100)
        df_signal = fetch_ohlcv(symbol, '1h', 100)

        # Check if fetching data failed
        if df_diff is None or df_signal is None:
            return  # Skip if data fetch failed

        # Calculate indicators with specified MACD parameters
        df_diff = calculate_indicators(df_diff, {'slow': 26, 'fast': 12, 'signal': 11})  # diff
        df_signal = calculate_indicators(df_signal, {'slow': 39, 'fast': 19, 'signal': 10})  # signal

        # Fetch balance and ticker
        balance = exchange.fetch_balance()
        ticker = exchange.fetch_ticker(symbol)
        btc_price = ticker['last']

        # Convert balances 
        usdc_balance = balance['free']['USDC'] 
        btc_balance = balance['free']['BTC']
        btc_balance_usdc_value = btc_balance * btc_price

        # Determine if we're in a position based on value comparison
        in_position = btc_balance_usdc_value > usdc_balance

        # Get higher timeframe confirmation 
        signal_positive = df_signal.iloc[-2]['macd_signal'] > 0 

        # Buy conditions
        if signal_positive and (df_diff.iloc[-2]['macd_diff'] > 0) and (df_diff.iloc[-3]['macd_diff'] < 0) and not in_position:
            if usdc_balance > 0:
                btc_amount = usdc_balance / btc_price
                if btc_amount > 0:
                    if place_order('buy', btc_amount * order_buffer_pct):
                        total_balance = btc_balance_usdc_value + usdc_balance
                        print(f"BUY | Total Balance (USDC): {total_balance:.2f} | Time: {datetime.now(timezone)}")

        # Sell conditions
        elif (df_diff.iloc[-2]['macd_diff'] < 0) and in_position:
            if btc_balance > 0:
                if place_order('sell', btc_balance * order_buffer_pct):
                    total_balance = btc_balance_usdc_value + usdc_balance
                    print(f"SELL | Total Balance (USDC): {total_balance:.2f} | Time: {datetime.now(timezone)}")

    except Exception as e:
        print(f"Error in trading strategy: {e}")

# Execute the trading strategy
check_conditions_and_trade()
