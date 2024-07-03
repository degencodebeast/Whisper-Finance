import pandas as pd
import pandas_ta as ta
import ccxt
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class BollingerBandsStrategy(Strategy):
    timeframe = '1h'
    sma_window = 20
    bollinger_length = 20
    bollinger_std_dev = 1 #or 2
    size = 1
    target = 0.05
    max_loss = -0.1

    def init(self):
        # self.exchange = ccxt.bitstamp()
        # self.symbol = 'SOL/USD'
        # self.df = self.fetch_ohlcv()
        # self.df['SMA'] = ta.sma(self.df['close'], length=self.sma_window)
        # self.bbands = ta.bbands(self.df['close'], length=self.bollinger_length, std=self.bollinger_std_dev)
        # self.df = pd.concat([self.df, self.bbands], axis=1)
        # self.df['BandWidth'] = self.df['BBU_' + str(self.bollinger_length)] - self.df['BBL_' + str(self.bollinger_length)]
        # self.df['Tight'] = self.df['BandWidth'] <= self.df['BandWidth'].quantile(0.2)

        self.exchange = ccxt.bitstamp()
        self.symbol = 'SOL/USD'
        self.df = self.fetch_ohlcv()
        self.df['SMA'] = ta.sma(self.df['close'], length=self.sma_window)
        self.bbands = ta.bbands(self.df['close'], length=self.bollinger_length, std=self.bollinger_std_dev)
        self.df = pd.concat([self.df, self.bbands], axis=1)
        self.df['BandWidth'] = self.bbands.iloc[:, 0] - self.bbands.iloc[:, 2]
        self.df['Tight'] = self.df['BandWidth'] <= self.df['BandWidth'].rolling(window=50).mean() * 0.9

    def fetch_ohlcv(self):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=500)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def next(self):
        # if not self.position and self.df['Tight'].iloc[-1]:
        #     if self.data.close[-1] > self.df['BBU_' + str(self.bollinger_length)].iloc[-1]:
        #         self.buy(sl=self.data.close[-1] * (1 + self.max_loss), tp=self.data.close[-1] * (1 + self.target))
        #     elif self.data.close[-1] < self.df['BBL_' + str(self.bollinger_length)].iloc[-1]:
        #         self.sell(sl=self.data.close[-1] * (1 - self.max_loss), tp=self.data.close[-1] * (1 - self.target))

        # elif not self.df['Tight'].iloc[-1]:
        #     if self.position:
        #         self.position.close()

        if not self.position and self.df['Tight'].iloc[-1]:
            if self.data.Close[-1] > self.bbands.iloc[-1, 0] * 0.998:
                self.buy(sl=self.data.Close[-1] * (1 + self.max_loss), tp=self.data.Close[-1] * (1 + self.target))
            elif self.data.Close[-1] < self.bbands.iloc[-1, 2] * 1.002:
                self.sell(sl=self.data.Close[-1] * (1 - self.max_loss), tp=self.data.Close[-1] * (1 - self.target))
        elif not self.df['Tight'].iloc[-1]:
            if self.position:
                self.position.close()

data = pd.read_csv('SOL-USD1h100.csv', index_col='datetime', parse_dates=True)

data = data.iloc[:, :5]

# Ensure the DataFrame contains columns 'Open', 'High', 'Low', 'Close', 'Volume'
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

bt = Backtest(data, BollingerBandsStrategy, cash=100000, commission=0.002, exclusive_orders=True)

stats = bt.run()

print(stats)

#bt.plot()