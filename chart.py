import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc

import numpy as np
import matplotlib.pyplot as plt
import datetime
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import num2date
from pymongo import MongoClient
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc

client = MongoClient('localhost', 27017)
db = client['stock']
collectStock = db['stock']

result = collectStock.find_one({'stockNo': '3443'})
details = result['details']

df = pd.DataFrame(list(details))
df = df.set_index(['date'])

#df['20ma'] = df['closePrice'].rolling(window=20, min_periods=0).mean()
#df['60ma'] = df['closePrice'].rolling(window=60, min_periods=0).mean()
df_ohlc = df['closePrice'].resample('20D').ohlc()
df_volume = df['dealValue'].resample('20D').sum()
df_ohlc.reset_index(inplace=True)

df_ohlc['date'] = df_ohlc['date'].map(mdates.date2num)

ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
ax1.xaxis_date()


candlestick_ohlc(ax1, df_ohlc.values, width=2, colorup='r')
ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)



#ax1.plot(df.index, df['closePrice'])
#ax1.plot(df.index, df['20ma'])
#ax1.plot(df.index, df['60ma'])
#ax2.bar(df.index, df['dealValue'])
plt.show()
