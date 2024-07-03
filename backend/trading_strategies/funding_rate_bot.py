import os
import time
import pandas as pd
import asyncio
from dotenv import load_dotenv
from kwenta import Kwenta
import pandas_ta as ta
from datetime import datetime, timedelta

load_dotenv()

# Configuration
symbol = 'sETH'  # Adjust as needed
timeframe = '5m'  # Changed to 5 minutes to match the backtest
funding_rate_threshold = -43
short_funding_rate_threshold = 32
take_profit = 0.06
max_loss = 0.08
leverage = 3

# Kwenta setup
provider_rpc = os.environ.get('PROVIDER_RPC_URL')
wallet_address = os.environ.get('WALLET_ADDRESS')
private_key = os.environ.get('PRIVATE_KEY')

kwenta = Kwenta(provider_rpc=provider_rpc, wallet_address=wallet_address, private_key=private_key)
sm_account = kwenta.get_sm_accounts()[0]

async def get_funding_rate(symbol):
    # This function needs to be implemented based on Kwenta SDK capabilities
    # For now, we'll use a placeholder
    funding_rate = await kwenta.get_funding_rate(symbol)
    return funding_rate

async def get_current_price(symbol):
    price_data = await kwenta.get_current_asset_price(symbol)
    return float(price_data['price'])

async def get_position(symbol):
    position = await kwenta.get_current_position(symbol, wallet_address=sm_account)
    in_pos = position['size'] != 0
    size = float(position['size'])
    entry_price = float(position['average_entry'])
    pnl_perc = float(position['pnl_percent'])
    long = size > 0
    return in_pos, size, entry_price, pnl_perc, long

async def open_position(symbol, is_long, size, take_profit, stop_loss):
    current_price = await get_current_price(symbol)
    tp_price = current_price * (1 + take_profit) if is_long else current_price * (1 - take_profit)
    sl_price = current_price * (1 - max_loss) if is_long else current_price * (1 + max_loss)
    
    try:
        if is_long:
            order = await kwenta.open_position(
                symbol, sm_account, short=False, leverage_multiplier=leverage,
                size=size, take_profit_price=tp_price, stop_loss_price=sl_price
            )
        else:
            order = await kwenta.open_position(
                symbol, sm_account, short=True, leverage_multiplier=leverage,
                size=size, take_profit_price=tp_price, stop_loss_price=sl_price
            )
        print(f"{'Long' if is_long else 'Short'} position opened: {order}")
        return order
    except Exception as e:
        print(f"Error opening position: {e}")
        return None

async def close_position(symbol):
    try:
        result = await kwenta.close_position(symbol, sm_account, execute_now=True)
        print(f"Position closed: {result}")
        return result
    except Exception as e:
        print(f"Error closing position: {e}")
        return None

async def funding_rate_strategy():
    while True:
        try:
            funding_rate = await get_funding_rate(symbol)
            current_price = await get_current_price(symbol)
            in_position, position_size, entry_price, pnl_perc, is_long = await get_position(symbol)

            print(f"Current funding rate: {funding_rate}")
            print(f"Current price: {current_price}")
            print(f"In position: {in_position}, PnL: {pnl_perc}%")

            if not in_position:
                if funding_rate < funding_rate_threshold:
                    # Open long position
                    await open_position(symbol, True, 1, take_profit, max_loss)
                elif funding_rate > short_funding_rate_threshold:
                    # Open short position
                    await open_position(symbol, False, 1, take_profit, max_loss)
            else:
                # Check if take profit or stop loss hit (assuming Kwenta handles this automatically)
                # We'll add an additional check here for safety
                if (is_long and pnl_perc >= take_profit * 100) or (not is_long and pnl_perc <= -take_profit * 100):
                    print("Take profit hit, closing position")
                    await close_position(symbol)
                elif (is_long and pnl_perc <= -max_loss * 100) or (not is_long and pnl_perc >= max_loss * 100):
                    print("Stop loss hit, closing position")
                    await close_position(symbol)

        except Exception as e:
            print(f"An error occurred: {e}")

        await asyncio.sleep(300)  # Sleep for 5 minutes

async def main():
    while True:
        try:
            await funding_rate_strategy()
        except Exception as e:
            print(f"Error in main loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())