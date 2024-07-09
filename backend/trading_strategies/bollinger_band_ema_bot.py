import os
import asyncio
import logging
import pandas as pd
import pandas_ta as pd_ta
from dotenv import load_dotenv
from kwenta import Kwenta
from web3 import Web3

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
symbol = 'sETH'  # Adjust as needed for Kwenta
timeperiod = 20
ema_period = 20
take_profit = 1.1
stop_loss = 0.95
size = 1
leverage = 3  # Added leverage parameter

# Kwenta setup
provider_rpc = os.getenv('PROVIDER_RPC_URL')
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')

kwenta = Kwenta(provider_rpc=provider_rpc, wallet_address=wallet_address, private_key=private_key)
sm_account = kwenta.get_sm_accounts()[0]

async def get_position(symbol):
    try:
        position = await kwenta.get_current_position(symbol, wallet_address=sm_account)
        return position if float(position['size']) != 0 else None
    except Exception as e:
        logger.error(f"Error getting position: {e}")
        return None

async def limit_order(symbol, is_buy, sz, limit_px, reduce_only=False):
    try:
        if is_buy:
            order = await kwenta.open_limit(
                symbol, wallet_address=sm_account, short=False,
                leverage_multiplier=leverage, size=sz, price=limit_px
            )
        else:
            order = await kwenta.open_limit(
                symbol, wallet_address=sm_account, short=True,
                leverage_multiplier=leverage, size=sz, price=limit_px
            )
        logger.info(f"{'BUY' if is_buy else 'SELL'} order placed: {order}")
        return order
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return None

async def kill_switch(symbol):
    position = await get_position(symbol)
    while position:
        try:
            await kwenta.close_position(symbol, sm_account, execute_now=True)
            logger.info(f"Kill switch - {'SELL' if float(position['size']) > 0 else 'BUY'} TO CLOSE SUBMITTED")
            await asyncio.sleep(5)
            position = await get_position(symbol)
        except Exception as e:
            logger.error(f"Error in kill switch: {e}")
            await asyncio.sleep(5)
    logger.info('Position successfully closed in kill switch')

async def get_price_data(symbol, lookback_days=1):
    try:
        end_time = int(pd.Timestamp.now().timestamp() * 1000)
        start_time = end_time - (lookback_days * 24 * 60 * 60 * 1000)
        candles = await kwenta.queries.candles(symbol, time_back=lookback_days*24*60*60, period='5m')
        df = pd.DataFrame(candles)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['close'] = pd.to_numeric(df['close'])
        return df
    except Exception as e:
        logger.error(f"Error fetching price data: {e}")
        return pd.DataFrame()

async def bot(symbol):
    try:
        df = await get_price_data(symbol)
        if df.empty:
            logger.warning("No price data available")
            return

        close_price = df['close'].iloc[-1]

        bbands = pd_ta.bbands(df['close'], timeperiod=timeperiod, nbdevup=2, nbdevdn=2)
        upper_band = bbands['BBU_' + str(timeperiod)].iloc[-1]
        lower_band = bbands['BBL_' + str(timeperiod)].iloc[-1]

        ema = pd_ta.ema(df['close'], timeperiod=ema_period)
        ema_value = ema.iloc[-1]

        position = await get_position(symbol)

        if (close_price > upper_band) or (ema_value > close_price):
            if not position:
                logger.info('Buy signal triggered')
                await limit_order(symbol, True, size, close_price)
            else:
                logger.info('Already in position, skipping buy signal')

        elif close_price < ema_value:
            if position:
                logger.info('Sell signal triggered')
                await kill_switch(symbol)
                await limit_order(symbol, False, size * 2, close_price)
            else:
                logger.info('No position to sell')

    except Exception as e:
        logger.error(f"Error in bot: {e}")

async def main():
    try:
        # Initialize Kwenta client
        await kwenta.initialize()
        logger.info(f"Kwenta initialized for account: {sm_account}")

        while True:
            try:
                await bot(symbol)
                await asyncio.sleep(60)  # Run the bot every minute
            except Exception as e:
                logger.error(f"Error in bot iteration: {e}")
                await asyncio.sleep(60)
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    asyncio.run(main())