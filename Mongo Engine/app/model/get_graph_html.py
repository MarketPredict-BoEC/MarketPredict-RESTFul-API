import pandas as pd
import plotly.offline as po
import pandas_datareader.data as web
import plotly.graph_objs as go
from app.model.candleModel import CandleModel
from  datetime import datetime


import datetime


def marketData():
    try:
        obj = CandleModel()
        data = obj.find_by_date_symbol_resolution(symbol="EURUSD", resolution="1", start=1617391140, end=1617936840)
        df = pd.DataFrame(data=data)
        print(df['timestamp'])
        df['Date'] = [datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                        , '%Y-%m-%d %H:%M:%S') for ts in df['timestamp']]
        print(df['date'])
        df = df.drop('timestamp', 1)
        df = df.set_index('date')
        print(df.columns)
        return df
    except:
        return None


def get_graph(search, start):
    try:
        sid = search
        sd = start
        ed = datetime.datetime.now()

        df = web.DataReader(sid, 'yahoo', sd, ed)
        print(df)
        df.columns = ['high', 'low', 'open','close','volume','adj close']
        if df is not None:
            print("df ok")
            SMA5 = df['close'].rolling(5).mean()
            SMA10 = df['close'].rolling(10).mean()
            SMA20 = df['close'].rolling(20).mean()
            SMA60 = df['close'].rolling(60).mean()
            trace = go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                                   name='K')
            s5 = go.Scatter(x=SMA5.index, y=SMA5.values, name='5MA')
            s10 = go.Scatter(x=SMA10.index, y=SMA10.values, name='10MA')
            s20 = go.Scatter(x=SMA20.index, y=SMA20.values, name='20MA')
            s60 = go.Scatter(x=SMA60.index, y=SMA60.values, name='60MA')
            data = [trace, s5, s10, s20, s60]
            layout = {'title': sid}
            fig = dict(data=data, layout=layout)
            po.plot(fig, filename='templates/stock_test.html', auto_open=False)

            return True
        else:

            return False
    except:
        return False
