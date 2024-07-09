from kwenta import Kwenta
import os
import time
import pandas as pd
import asyncio
import schedule
import threading
import sys
import pandas_ta as pd_ta
from datetime import datetime, timedelta
import requests
import json
from eth_account.signers.local import LocalAccount
import eth_account
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

# Configuration
symbol = 'sETH'  # Assuming sETH as an example, adjust as needed
timeframe = '15m'
sma_window = 20
lookback_days = 1
size = 1
target = 5
max_loss = -10
leverage = 3
max_positions = 1

# get env variables
provider_rpc = os.environ.get('PROVIDER_RPC_URL')
wallet_address = os.environ.get('WALLET_ADDRESS')
private_key = os.environ.get('PRIVATE_KEY')

# # Load the secret key from the keypath file
# with open(os.path.expanduser(keypath), "r") as f:
#     secret = json.load(f)
# kp = Keypair.from_bytes(bytes(secret))
# #kp = load_keypair(f)  
# print("using public key:", kp.pubkey())
# config = configs[env]
# wallet = Wallet(kp)

# kwenta = Kwenta(provider_rpc=provider_rpc, wallet_address=wallet_address, private_key=private_key)
# sm_account = kwenta.get_sm_accounts()[0]

async def adjust_leverage_size_signal(symbol, leverage, wallet_address):
    print('leverage:', leverage)
    try:
        result = await kwenta.get_leveraged_amount(symbol, leverage, wallet_address)
        
        leveraged_amount = float(result["leveraged_amount"])
        max_asset_leverage = float(result["max_asset_leverage"])

        print(f"Max asset leverage: {max_asset_leverage}")
        print(f"Leveraged amount: {leveraged_amount}")

        return max_asset_leverage, leveraged_amount
    except Exception as e:
        print(f"Error in adjust_leverage_size_signal: {e}")
        return None, None
    
async def ask_bid(symbol, slippage_tolerance=0.02):  # 2.0% default slippage tolerance
    try:
        price_data = await kwenta.get_current_asset_price(symbol)
        current_price = float(price_data['price'])
        
        # Simulated spread (keeping it small for price estimation)
        spread = current_price * 0.0002  # 0.02% spread
        
        # Calculate simulated ask and bid prices
        ask = current_price + (spread / 2)
        bid = current_price - (spread / 2)
        
        # Calculate slippage-adjusted prices
        max_ask = ask * (1 + slippage_tolerance)
        min_bid = bid * (1 - slippage_tolerance)
        
        print(f"Current price: {current_price}")
        print(f"Ask: {ask}, Max Ask (with slippage): {max_ask}")
        print(f"Bid: {bid}, Min Bid (with slippage): {min_bid}")
        
        return ask, bid, max_ask, min_bid
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None, None, None, None

async def limit_order(symbol, is_buy, size, limit_price):
    #rounding = (await get_sz_px_decimals(coin))[0]
    #sz = round(sz, rounding)
    print(f'placing limit order for {symbol} {size} @ {limit_price}')
    
    try:
        if is_buy:
            order = await kwenta.open_limit(symbol, wallet_address=sm_account, short=False, leverage_multiplier=leverage, size=size, price=limit_price)
        else:
            order = await kwenta.open_limit(symbol, wallet_address=sm_account, short=True, leverage_multiplier=leverage, size=size, price=limit_price)
        
        print(f"{'BUY' if is_buy else 'SELL'} order placed: {order}")
        return order
    except Exception as e:
        print(f"Error placing order: {e}")
        return None

async def acct_bal(wallet_address):
    balance = await kwenta.get_susd_balance(wallet_address)
    print(f'Current account value: {balance["balance_usd"]}')
    return float(balance['balance_usd'])


async def get_position(symbol):
    # web3 = kwenta.web3
    # position = await kwenta.get_current_position(symbol, wallet_address=sm_account)
    # in_pos = position['size'] != 0
    # size = float(position['size'])
    # size_ether = float(web3.from_wei(abs(size), "ether")) 
    # pos_symbol = symbol
    # entry_price_wei = position['last_price']
    # entry_price_usd = float(web3.from_wei(entry_price_wei, 'ether'))
    # pnl_perc = float(position['pnl_usd'])
    # long = size > 0
    # return [position], in_pos, size_ether, pos_symbol, entry_price_usd, pnl_perc, long

    web3 = kwenta.web3
    position = await kwenta.get_current_position(symbol, wallet_address=sm_account)
    in_pos = position['size'] != 0
    size = float(position['size'])
    size_ether = float(web3.from_wei(abs(size), "ether"))
    pos_symbol = symbol
    entry_price_wei = position['last_price']
    entry_price_usd = float(web3.from_wei(entry_price_wei, 'ether'))
    pnl_usd = float(position['pnl_usd'])
    long = size > 0

    # Get current price
    current_price_data = await kwenta.get_current_asset_price(symbol)
    current_price_usd = float(current_price_data['price'])

    # Calculate position value at entry
    position_value_at_entry = abs(size_ether) * entry_price_usd

    # Calculate PNL percentage
    if position_value_at_entry != 0:
        pnl_perc = (pnl_usd / position_value_at_entry) * 100
    else:
        pnl_perc = 0

    # Ensure the sign of pnl_perc is correct
    if (long and current_price_usd < entry_price_usd) or (not long and current_price_usd > entry_price_usd):
        pnl_perc = -abs(pnl_perc)
    else:
        pnl_perc = abs(pnl_perc)

    return [position], in_pos, size_ether, pos_symbol, entry_price_usd, pnl_perc, long


async def check_market_orders(token_symbol):
    delayed_order = kwenta.check_delayed_orders(token_symbol, sm_account)
    
    if delayed_order['is_open']:
        web3 = kwenta.web3
        size = float(delayed_order['position_size'])
        size_ether = float(web3.from_wei(abs(size), "ether"))
        price_in_wei = float(delayed_order['desired_fill_price'])
        price = float(web3.from_wei(price_in_wei, 'ether'))
        return {
            'market': token_symbol,
            'size': size_ether,
            'price': price,
            'type': 'Delayed' if delayed_order['executable_time'] > 0 else 'Limit',
            'intention_time': delayed_order['intention_time'],
            'executable_time': delayed_order['executable_time']
        }
    return None

async def get_unexecuted_open_orders(account):
    unexecuted_orders = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_market = {executor.submit(check_market_orders, kwenta, market, account): market 
                            for market in kwenta.markets}
        
        for future in as_completed(future_to_market):
            result = future.result()
            if result:
                unexecuted_orders.append(result)
    
    return unexecuted_orders

async def cancel_all_orders(account):
    cancelled_orders = []
    
    for token_symbol in kwenta.markets:
        try:
            delayed_order = kwenta.check_delayed_orders(token_symbol, account)
            if delayed_order["is_open"]:
                result = kwenta.cancel_order(token_symbol, account, execute_now=True)
                if result:
                    cancelled_orders.append({
                        'token': token_symbol,
                        'tx_hash': result
                    })
                    print(f'Cancelled order for {token_symbol}. TX: {result}')
                else:
                    print(f'Failed to cancel order for {token_symbol}')
        except Exception as e:
            print(f"Error cancelling order for {token_symbol}: {e}")
    
    if cancelled_orders:
        print(f'Cancelled {len(cancelled_orders)} orders')
    else:
        print('No open orders to cancel')
    
    return cancelled_orders


# async def cancel_all_orders(account):
#     try:
#         await kwenta.cancel_all_orders(account)
#         print('All orders have been cancelled')
#     except Exception as e:
#         print(f"Error cancelling orders: {e}")

async def kill_switch(symbol, account):
    position, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(symbol)
    while im_in_pos:
        await cancel_all_orders(account)
        ask, bid, _ = await ask_bid(pos_sym)
        pos_size = abs(pos_size)
        if long:
            await limit_order(pos_sym, False, pos_size, ask, True, account)
            print('Kill switch - SELL TO CLOSE SUBMITTED')
        else:
            await limit_order(pos_sym, True, pos_size, bid, True, account)
            print('Kill switch - BUY TO CLOSE SUBMITTED')
        await asyncio.sleep(5)
        position, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(symbol)
    print('Position successfully closed in the kill switch')

async def pnl_close(symbol, target, max_loss, account):
    print('Starting PNL close')
    position, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(symbol)
    if pnl_perc > target:
        print(f'PNL gain is {pnl_perc} and target is {target}... closing position WIN')
        await kill_switch(pos_sym, account)
    elif pnl_perc <= max_loss:
        print(f'PNL loss is {pnl_perc} and max loss is {max_loss}... closing position LOSS')
        await kill_switch(pos_sym, account)
    else:
        print(f'PNL is {pnl_perc}, max loss is {max_loss}, and target is {target}... not closing position')
    print('Finished with PNL close')


async def close_all_positions(account):
    closed_positions = []

    for market in kwenta.markets:
        try:
            position = await kwenta.get_current_position(market, wallet_address=account)
            if position['size'] != 0:  # If there's an open position
                await kill_switch(market, account)
                closed_positions.append(market)
                print(f"Closed position for {market}")
        except Exception as e:
            print(f"Error closing position for {market}: {e}")

    if closed_positions:
        print(f"Closed positions in the following markets: {', '.join(closed_positions)}")
    else:
        print("No open positions to close")

    return closed_positions

async def calculate_bollinger_bands(df, length=20, std_dev=2):
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    bollinger_bands = pd_ta.bbands(df['close'], length=length, std=std_dev)
    df = pd.concat([df, bollinger_bands], axis=1)
    df['BandWidth'] = df['BBU_20_2.0'] - df['BBL_20_2.0']
    tight_threshold = df['BandWidth'].quantile(0.2)
    wide_threshold = df['BandWidth'].quantile(0.8)
    current_band_width = df['BandWidth'].iloc[-1]
    tight = current_band_width <= tight_threshold
    wide = current_band_width >= wide_threshold
    return df, tight, wide

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

async def get_ohlcv(symbol, interval, lookback_days):
    end_time = int(time.time() * 1000)
    start_time = end_time - (lookback_days * 24 * 60 * 60 * 1000)
    candles = await kwenta.queries.candles(symbol, time_back=lookback_days*24*60*60, period=interval)
    return candles

async def calculate_sma(prices, window):
    return prices.rolling(window=window).mean().iloc[-1]

async def get_latest_sma(symbol, interval, window, lookback_days=1):
    candles = await get_ohlcv(symbol, interval, lookback_days)
    df = await process_data_to_df(candles)
    if not df.empty:
        return await calculate_sma(df['close'], window)
    else:
        return None

async def supply_demand_zones_hl(symbol, timeframe, limit):
    print('Starting supply and demand zone calculations...')
    
    sd_df = pd.DataFrame()
    
    candles = await get_ohlcv(symbol, timeframe, limit)
    df = await process_data_to_df(candles)
    
    if df.empty:
        print("No data available for supply and demand zones calculation")
        return sd_df

    supp = df['support'].iloc[-1]
    resis = df['resis'].iloc[-1]

    df['supp_lo'] = df['low'].rolling(window=3, center=True).min()
    supp_lo = df['supp_lo'].iloc[-1]

    df['res_hi'] = df['high'].rolling(window=3, center=True).max()
    res_hi = df['res_hi'].iloc[-1]

    sd_df[f'{timeframe}_dz'] = [supp_lo, supp]
    sd_df[f'{timeframe}_sz'] = [res_hi, resis]

    print('Here are the supply and demand zones:')
    print(sd_df)

    return sd_df

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
    
async def bot():
    print("running bot")
    pos_size = size 
    # account = eth_account.Account.from_key(private_key)
    # account1 = account.address
    #account1 = wallet_address  # Using the wallet address instead of creating a new account object
    account1 = sm_account
    positions1, im_in_pos, mypos_size, pos_sym1, entry_px1, pnl_perc1, long1, num_of_pos = await get_position(symbol)
    print(f'These are the positions {positions1}')

    if im_in_pos:
        print('In position so checking PNL close')
        await pnl_close(symbol, target, max_loss, account1)
    else:
        print('Not in position so no PNL close')

    # Check if in a partial position
    if 0 < mypos_size < pos_size:
        print(f'Current size {mypos_size}')
        pos_size = pos_size - mypos_size
        print(f'Updated size needed {pos_size}')
        im_in_pos = False 
    else:
        pos_size = size 

    latest_sma = await get_latest_sma(symbol, timeframe, sma_window, 2)

    if latest_sma is not None:
        print(f'Latest SMA for {symbol} over the {sma_window} intervals: {latest_sma}')
    else:
        print('Could not receive SMA')

    price = (await ask_bid(symbol))[0]

      # Check for unexecuted open orders
    open_orders = get_unexecuted_open_orders(account1, account1.wallet_address)
    print("Unexecuted Open Orders:")
    for order in open_orders:
        print(f"Market: {order['market']}")
        print(f"Type: {order['type']}")
        print(f"Size: {order['size']}")
        print(f"Price: {order['price']}")
        print("---")

    if not im_in_pos and not open_orders:
        sd_df = await supply_demand_zones_hl(symbol, timeframe, lookback_days)

        print(sd_df)

        sd_df[f'{timeframe}_dz'] = pd.to_numeric(sd_df[f'{timeframe}_dz'], errors='coerce')
        sd_df[f'{timeframe}_sz'] = pd.to_numeric(sd_df[f'{timeframe}_sz'], errors='coerce')

        buy_price = sd_df[f'{timeframe}_dz'].mean()
        sell_price = sd_df[f'{timeframe}_sz'].mean()

        # Make buy price and sell price a float
        buy_price = float(buy_price)
        sell_price = float(sell_price)

        print(f'Current price {price}, buy price {buy_price}, sell price {sell_price}')

        # Calculate the absolute diff between the current price and buy/sell prices
        diff_to_buy_price = abs(price - buy_price)
        diff_to_sell_price = abs(price - sell_price)

        # Determine whether to buy or sell based on which price is closer
        if diff_to_buy_price < diff_to_sell_price:
            await cancel_all_orders(account1)
            print('Canceled all orders...')

            # Enter the buy price
            await limit_order(symbol, True, pos_size, buy_price, False, account1)
            print(f'Just placed order for {pos_size} at {buy_price}')

        else:
            # Enter sell order
            print('Placing sell order')
            await cancel_all_orders(account1)
            print('Just canceled all orders')
            await limit_order(symbol, False, pos_size, sell_price, False, account1)
            print(f'Just placed an order for {pos_size} at {sell_price}')

    else:
        print(f'In {pos_sym1} position size {mypos_size} so not entering')

# Main execution
async def main():
    while True:
        try:
            await bot()
            await asyncio.sleep(30)
        except Exception as e:
            print(f'*** Error occurred: {e}. Sleeping 30 seconds and retrying...')
            await asyncio.sleep(30)

if __name__ == "__main__":

    kwenta = Kwenta(provider_rpc=provider_rpc, wallet_address=wallet_address, private_key=private_key)
    sm_account = kwenta.get_sm_accounts()[0]

    asyncio.run(main())




# async def kill_switch(symbol, account):
#     try:
#         await kwenta.close_position(symbol, account, execute_now=True)
#         print(f"Position in {symbol} closed successfully")
#     except Exception as e:
#         print(f"Error in kill switch for {symbol}: {e}")

# # Usage in your bot function
# async def bot():
#     # ... (other bot logic)

#     # When you need to close all positions
#     closed_positions = await close_all_positions(kwenta, account1)

#     # ... (rest of bot logic)

# async def close_all_positions(account):
#     all_positions = await kwenta.get_all_positions(wallet_address=account)
#     for position in all_positions:
#         if float(position['size']) != 0:
#             await kill_switch(position['asset'], account)
#     print('All positions have been closed')


# async def ask_bid(symbol):
#     try:
#         # Get the current price from Kwenta
#         price_data = await kwenta.get_current_asset_price(symbol)
        
#         # Extract the current price
#         current_price = float(price_data['price'])
        
#         # Calculate a simulated spread
#         spread = current_price * 0.0002  # 0.02% spread, adjust as needed
        
#         # Calculate simulated ask and bid prices
#         ask = current_price + (spread / 2)
#         bid = current_price - (spread / 2)
        
#         return ask, bid, None  # Still returning None for l2_data as it's not applicable
#     except Exception as e:
#         print(f"Error fetching price for {symbol}: {e}")
#         return None, None, None
    
    # price_data = await kwenta.get_current_asset_price(symbol)
    # ask = float(price_data['ask'])
    # bid = float(price_data['bid'])
    # return ask, bid, None  # Returning None for l2_data as it's not directly available


# async def get_position_andmaxpos(symbol, account, max_positions):
#     all_positions = await kwenta.get_all_positions(wallet_address=account)
#     open_positions = [pos for pos in all_positions if float(pos['size']) != 0]
    
#     num_of_pos = len(open_positions)
#     print(f'Current account value: {await acct_bal(account)}')
    
#     if num_of_pos > max_positions:
#         print(f'We are in {num_of_pos} positions and max pos is {max_positions}... closing positions')
#         for position in open_positions:
#             await kill_switch(position['asset'], account)
#     else:
#         print(f'We are in {num_of_pos} positions and max pos is {max_positions}... not closing positions')

#     position = next((pos for pos in open_positions if pos['asset'] == symbol), None)
#     if position:
#         in_pos = True
#         size = float(position['size'])
#         pos_sym = position['asset']
#         entry_px = float(position['average_entry'])
#         pnl_perc = float(position['pnl_percent'])
#         long = size > 0
#     else:
#         in_pos = False
#         size = 0
#         pos_sym = None
#         entry_px = 0
#         pnl_perc = 0
#         long = None

#     return [position], in_pos, size, pos_sym, entry_px, pnl_perc, long, num_of_pos


# async def bot():
#     account1 = eth_account.Account.from_key(private_key)
#     leverage, size = await adjust_leverage_size_signal(symbol, leverage, account1.address)
    
#     positions1, im_in_pos, mypos_size, pos_sym1, entry_px1, pnl_perc1, long1, num_of_pos = await get_position_andmaxpos(symbol, account1.address, max_positions)
#     print(f'These are the positions {positions1}')

#     if im_in_pos:
#         print('In position so checking PNL close')
#         await pnl_close(symbol, target, max_loss, account1.address)
#     else:
#         print('Not in position so no PNL close')

#     pos_size = size - mypos_size if 0 < mypos_size < size else size

#     latest_sma = await get_latest_sma(symbol, timeframe, sma_window, 2)
#     if latest_sma is not None:
#         print(f'Latest SMA for {symbol} over the {sma_window} intervals: {latest_sma}')
#     else:
#         print('Could not receive SMA')

#     price = (await ask_bid(symbol))[0]

#     if not im_in_pos:
#         sd_df = await supply_demand_zones_hl(symbol, timeframe, lookback_days)
#         print(sd_df)

#         sd_df[f'{timeframe}_dz'] = pd.to_numeric(sd_df[f'{timeframe}_dz'], errors='coerce')
#         sd_df[f'{timeframe}_sz'] = pd.to_numeric(sd_df[f'{timeframe}_sz'], errors='coerce')

#         buy_price = sd_df[f'{timeframe}_dz'].mean()
#         sell_price = sd_df[f'{timeframe}_sz'].mean()

#         buy_price = float(buy_price)
#         sell_price = float(sell_price)

#         print(f'Current price {price}, buy price {buy_price}, sell price {sell_price}')

#         diff_to_buy_price = abs(price - buy_price)
#         diff_to_sell_price = abs(price - sell_price)

#         if diff_to_buy_price < diff_to_sell_price:
#             await cancel_all_orders(account1.address)
#             print('Canceled all orders...')
#             await limit_order(symbol, True, pos_size, buy_price, False, account1.address)
#             print(f'Just placed order for {pos_size} at {buy_price}')
#         else:
#             print('Placing sell order')
#             await cancel_all_orders(account1.address)
#             print('Just canceled all orders')
#             await limit_order(symbol, False, pos_size, sell_price, False, account1.address)
#             print(f'Just placed an order for {pos_size} at {sell_price}')
#     else:
#         print(f'In {pos_sym1} position size {mypos_size} so not entering')

# async def main():
#     while True:
#         try:
#             await bot()
#             await asyncio.sleep(30)
#         except Exception as e:
#             print(f'*** Error occurred: {e}. Sleeping 30 seconds and retrying...')
#             await asyncio.sleep(30)

# if __name__ == "__main__":
#     asyncio.run(main())