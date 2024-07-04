import os
import time
import pandas as pd
import asyncio
import schedule
import pandas_ta as ta
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kwenta import Kwenta
from web3 import Web3

load_dotenv()

# Configuration
symbol = 'sETH'  # Adjust as needed for Kwenta
timeframe = '15m'
sma_window = 20
lookback_days = 1
size = 1
target = 5
max_loss = -10
leverage = 3
max_positions = 1

# Kwenta setup
provider_rpc = os.environ.get('PROVIDER_RPC_URL')
wallet_address = os.environ.get('WALLET_ADDRESS')
private_key = os.environ.get('PRIVATE_KEY')

kwenta = Kwenta(provider_rpc=provider_rpc, wallet_address=wallet_address, private_key=private_key)
sm_account = kwenta.get_sm_accounts()[0]

async def ask_bid(symbol):
    price_data = await kwenta.get_current_asset_price(symbol)
    ask = float(price_data['ask'])
    bid = float(price_data['bid'])
    return ask, bid, None  # Returning None for l2_data as it's not directly available in Kwenta

async def get_sz_px_decimals(symbol):
    # This function might need adjustment based on Kwenta's specifics
    # For now, we'll return some default values
    return 6, 18  # Assuming 6 decimals for size and 18 for price (wei)

async def limit_order(coin, is_buy, sz, limit_px, reduce_only):
    try:
        if is_buy:
            order = await kwenta.open_limit(
                coin, wallet_address=sm_account, short=False,
                leverage_multiplier=leverage, size=sz, price=limit_px
            )
        else:
            order = await kwenta.open_limit(
                coin, wallet_address=sm_account, short=True,
                leverage_multiplier=leverage, size=sz, price=limit_px
            )
        print(f"{'BUY' if is_buy else 'SELL'} order placed: {order}")
        return order
    except Exception as e:
        print(f"Error placing order: {e}")
        return None

async def acct_bal():
    balance = await kwenta.get_susd_balance(sm_account)
    print(f"Current account value: {balance['balance_usd']}")
    return float(balance['balance_usd'])

async def adjust_leverage_size_signal(symbol, leverage):
    account_value = await acct_bal()
    acct_val95 = account_value * 0.95
    price = (await ask_bid(symbol))[0]
    size = (acct_val95 / price) * leverage
    size = float(size)
    rounding, _ = await get_sz_px_decimals(symbol)
    size = round(size, rounding)
    return leverage, size

async def get_position(symbol):
    position = await kwenta.get_current_position(symbol, wallet_address=sm_account)
    in_pos = position['size'] != 0
    size = float(position['size'])
    pos_sym = symbol
    entry_px = float(position['average_entry'])
    pnl_perc = float(position['pnl_percent'])
    long = size > 0
    return [position], in_pos, size, pos_sym, entry_px, pnl_perc, long

async def cancel_all_orders():
    try:
        await kwenta.cancel_all_orders(sm_account)
        print('All orders have been cancelled')
    except Exception as e:
        print(f"Error cancelling orders: {e}")

async def kill_switch(symbol):
    position, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(symbol)
    while im_in_pos:
        await cancel_all_orders()
        ask, bid, _ = await ask_bid(pos_sym)
        pos_size = abs(pos_size)
        if long:
            await limit_order(pos_sym, False, pos_size, ask, True)
        else:
            await limit_order(pos_sym, True, pos_size, bid, True)
        await asyncio.sleep(5)
        position, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(symbol)
    print('Position successfully closed in kill switch')

async def pnl_close(symbol, target, max_loss):
    position, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(symbol)
    if pnl_perc > target:
        print(f'PNL gain is {pnl_perc} and target is {target}. Closing position as a WIN')
        await kill_switch(pos_sym)
    elif pnl_perc <= max_loss:
        print(f'PNL loss is {pnl_perc} and max loss is {max_loss}. Closing position as a LOSS')
        await kill_switch(pos_sym)
    else:
        print(f'PNL is {pnl_perc}, max loss is {max_loss}, target is {target}. Not closing')

async def close_all_positions():
    for market in kwenta.markets:
        position = await kwenta.get_current_position(market, wallet_address=sm_account)
        if position['size'] != 0:
            await kill_switch(market)
    print('All positions have been closed')

async def get_ohlcv(symbol, interval, lookback_days):
    end_time = int(time.time() * 1000)
    start_time = end_time - (lookback_days * 24 * 60 * 60 * 1000)
    candles = await kwenta.queries.candles(symbol, time_back=lookback_days*24*60*60, period=interval)
    return candles

async def process_data_to_df(candles):
    if candles:
        df = pd.DataFrame(candles)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['support'] = df['close'].rolling(window=3, center=True).min()
        df['resis'] = df['close'].rolling(window=3, center=True).max()
        return df
    else:
        return pd.DataFrame()

async def calculate_bollinger_bands(df, length=20, std_dev=2):
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    bollinger_bands = ta.bbands(df['close'], length=length, std=std_dev)
    df = pd.concat([df, bollinger_bands], axis=1)
    df['BandWidth'] = df['BBU_20_2.0'] - df['BBL_20_2.0']
    tight_threshold = df['BandWidth'].quantile(0.2)
    wide_threshold = df['BandWidth'].quantile(0.8)
    current_band_width = df['BandWidth'].iloc[-1]
    tight = current_band_width <= tight_threshold
    wide = current_band_width >= wide_threshold
    return df, tight, wide

async def bot():
    lev, pos_size = await adjust_leverage_size_signal(symbol, leverage)
    pos_size = pos_size / 2  # Dividing position by 2

    positions, im_in_pos, mypos_size, pos_sym, entry_px, pnl_perc, long = await get_position(symbol)
    print(f'These are positions for {symbol}: {positions}')

    if im_in_pos:
        await cancel_all_orders()
        print('In position, checking PNL close')
        await pnl_close(symbol, target, max_loss)
    else:
        print('Not in position, no PNL close needed')

    ask, bid, _ = await ask_bid(symbol)
    print(f'Ask: {ask}, Bid: {bid}')

    snapshot_data = await get_ohlcv('sETH', '1m', 500)
    df = await process_data_to_df(snapshot_data)
    bbdf, bollinger_bands_tight = await calculate_bollinger_bands(df)

    print(f'Bollinger bands are tight: {bollinger_bands_tight}')

    if not im_in_pos and bollinger_bands_tight:
        print('Bollinger bands are tight and we don\'t have a position, so entering')
        await cancel_all_orders()
        print('Canceled all orders')

        # Enter buy order
        await limit_order(symbol, True, pos_size, bid, False)
        print(f'Placed buy order for {pos_size} at {bid}')

        # Enter sell order
        await limit_order(symbol, False, pos_size, ask, False)
        print(f'Placed sell order for {pos_size} at {ask}')

    elif not bollinger_bands_tight:
        await cancel_all_orders()
        await close_all_positions()
    else:
        print(f'Our position is {im_in_pos}, Bollinger bands may not be tight')

async def main():
    while True:
        try:
            await bot()
            await asyncio.sleep(30)
        except Exception as e:
            print(f'Error occurred: {e}. Sleeping 30 seconds and retrying...')
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())