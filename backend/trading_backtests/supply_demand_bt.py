'''
Start                     2022-05-19 18:00:00
End                       2024-04-18 17:00:00
Duration                    699 days 23:00:00
Exposure Time [%]                   99.553439
Equity Final [$]                  134469.2846
Equity Peak [$]                  137596.77034
Return [%]                          34.469285
Buy & Hold Return [%]              160.281262
Return (Ann.) [%]                   16.533772
Volatility (Ann.) [%]               31.091945
Sharpe Ratio                          0.53177
Sortino Ratio                        0.972723
Calmar Ratio                         0.548642
Max. Drawdown [%]                  -30.135827
Avg. Drawdown [%]                   -1.907053
Max. Drawdown Duration      534 days 22:00:00
Avg. Drawdown Duration       12 days 17:00:00
# Trades                                  365
Win Rate [%]                        25.753425
Best Trade [%]                      23.511842
Worst Trade [%]                    -13.625907
Avg. Trade [%]                       0.107872
Max. Trade Duration          24 days 09:00:00
Avg. Trade Duration           1 days 21:00:00
Profit Factor                        1.129975
Expectancy [%]                       0.401765
SQN                                  0.946203
'''

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as pd_ta
import ccxt
import warnings
warnings.filterwarnings('ignore')

class SupplyDemandZoneStrategy(Strategy):
    timeframe = '1h'
    limit = 1000
    max_loss = -0.03
    target = 0.12
    size = 0.25
    trail_percent = 0.05
    timeperiod = 20 
    ema_period = 20 


    def init(self):
        self.exchange = ccxt.coinbase()
        self.symbol = 'SOL/USD'
        self.df = self.fetch_ohlcv()
        self.zones = self.supply_demand_zones()
        self.buy_price = (self.zones['1h_dz'][0] + self.zones['1h_dz'][1]) / 2
        self.sell_price = (self.zones['1h_sz'][0] + self.zones['1h_sz'][1]) / 2

        # self.exchange = ccxt.bitstamp()
        # self.symbol = 'SOL/USD'
        # self.df = self.fetch_ohlcv()
        # self.zones = self.supply_demand_zones()
        # self.buy_price = self.zones['1h_dz'][1]  # Use the upper bound of the demand zone
        # self.sell_price = self.zones['1h_sz'][0]  # Use the lower bound of the supply zone
        #self.rsi = self.I(lambda x: self.rsi_func(pd.Series(x)), self.data.Close)

    def rsi_func(self, x):
        change = x.diff()
        gain = change.where(change > 0, 0)
        loss = -change.where(change < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss.replace(0, 1)  # Handle division by zero
        return 100 - (100 / (1 + rs))

    def fetch_ohlcv(self):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=self.limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def supply_demand_zones(self):
        df = self.df.copy()
        df['support'] = df[:-2]['close'].min()
        df['resis'] = df[:-2]['close'].max()
        df['supp_lo'] = df[:-2]['low'].min()
        df['res_hi'] = df[:-2]['high'].max()
        sd_df = pd.DataFrame()
        sd_df['1h_dz'] = [df.iloc[-1]['supp_lo'], df.iloc[-1]['support']]
        sd_df['1h_sz'] = [df.iloc[-1]['res_hi'], df.iloc[-1]['resis']]
        return sd_df

    def next(self):
        price = self.data.Close[-1]

        if not self.position:
            if price <= self.buy_price:
                self.buy(size=self.size)
            elif price >= self.sell_price:
                self.sell(size=self.size)
        else:
            entry_price = self.trades[-1].entry_price if self.trades else None
            if self.position.is_long:
                if price <= entry_price * (1 + self.max_loss):
                    self.position.close()
                elif price >= entry_price * (1 + self.target):
                    self.position.close()
            else:  # Short position
                if price >= entry_price * (1 + abs(self.max_loss)):
                    self.position.close()
                elif price <= entry_price * (1 - self.target):
                    self.position.close()

        # price = self.data.Close[-1]

        # if not self.position:
        #     if price <= self.buy_price and self.rsi[-1] < 30:
        #         self.buy(size=self.size)
        #     elif price >= self.sell_price and self.rsi[-1] > 70:
        #         self.sell(size=self.size)
        # else:
        #     entry_price = self.trades[-1].entry_price if self.trades else None
        #     if self.position.is_long:
        #         trail_price = max(self.data.Close[-1] * (1 - self.trail_percent), entry_price)
        #         if price <= trail_price or price <= entry_price * (1 + self.max_loss):
        #             self.position.close()
        #         elif price >= entry_price * (1 + self.target):
        #             self.position.close()
        #     else:  # Short position
        #         trail_price = min(self.data.Close[-1] * (1 + self.trail_percent), entry_price)
        #         if price >= trail_price or price >= entry_price * (1 + abs(self.max_loss)):
        #             self.position.close()
        #         elif price <= entry_price * (1 - self.target):
        #             self.position.close()

data = pd.read_csv('SOL-USD1h100.csv', index_col='datetime', parse_dates=True)

data = data.iloc[:, :5]

# Ensure the DataFrame contains columns 'Open', 'High', 'Low', 'Close', 'Volume'
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# # Convert the "Datetime" column to datetime format and set it as the index
# data['Datetime'] = pd.to_datetime(data['Datetime'])
# data.set_index('Datetime', inplace=True)

bt = Backtest(data, SupplyDemandZoneStrategy, cash=100000, commission=0.002, exclusive_orders=True)

#stats = bt.run()
stats = bt.optimize(maximize='Equity Final [$]', timeperiod=range(30, 60, 5))

print(stats)

#bt.plot()