# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 19:18:04 2021

@author: Novin
"""
import requests
from datetime import datetime
import pandas as pd
import ta
import json
import numpy as np
from sklearn import preprocessing
import BoEC
import time
from datetime import timedelta
from collections import deque


max_L = 15
SEQ_LEN = 7
embedding_dim= 210
marketDelayWindow = SEQ_LEN * 60 * 60
delayForINdicators = SEQ_LEN * 60 * 60
SEQ_LEN_news = 7 * 60 * 60
FUTURE_PERIOD_PREDICT = 1

def prepaireLongCandleData(category, pair, startDate, endDate):
    marketDF = pd.DataFrame()
    end = 0
    start = startDate
    if category.lower() == "forex":
        symbol = 'OANDA:'
        symbol = symbol + pair[0:2].upper() + '_' + pair[2:].upper()
    elif category.lower() == "cryptocurrency":
        symbol = 'BINANCE:'
        if pair.upper().find('BTCUSD'):
            symbol = symbol + pair.upper() + 'T'
            category = 'crypto'
    queryString = 'https://finnhub.io/api/v1/' + category.lower() + '+/candle?+symbol=' + symbol + '&resolution=60&from='
    queryString += str(startDate) + '&to=' + str(endDate) + '&token=bveu6qn48v6rhdtufjbg'

    while (end < endDate):
        end = start + 2592000


        # print(endDate)

        r = requests.get(queryString)

        df = pd.DataFrame(r.json())

        df['Close'] = df['c']
        df = df.drop('c', 1)

        df['Open'] = df['o']
        df = df.drop('o', 1)

        df['Low'] = df['l']
        df = df.drop('l', 1)

        df['High'] = df['h']
        df = df.drop('h', 1)

        df = df.drop('s', 1)

        df['timestamp'] = df['t']
        df = df.drop('t', 1)

        df['Volume'] = df['v']
        df = df.drop('v', 1)

        df['Date'] = [datetime.utcfromtimestamp(ts).strftime('%Y-%m-%dT%H:%M') for ts in df['timestamp']]
        df = df.drop('timestamp', 1)
        marketDF = pd.concat([marketDF, df], ignore_index=True)
        time.sleep(50 / 1000)
        start = end + 3600


def prepaireCandels(category, pair, startDate, endDate):

    startDate = startDate - delayForINdicators
    # endDate = int(endDate)
    if category.lower() == "forex":
        symbol = 'OANDA:'
        symbol = symbol + pair[0:2].upper() + '_' + pair[2:].upper()
    elif category.lower() == "cryptocurrency":
        symbol = 'BINANCE:'
        if pair.upper().find('BTCUSD'):
            symbol = symbol + pair.upper() + 'T'
            category = 'crypto'

    # print(endDate)
    queryString = 'https://finnhub.io/api/v1/' + category.lower() + '+/candle?+symbol=' + symbol + '&resolution=60&from='
    queryString += str(startDate) + '&to=' + str(endDate) + '&token=bveu6qn48v6rhdtufjbg'

    # columns={'Close','High','Low','Open','Status','timestamp','Volume'}
    r = requests.get(queryString)

    df = pd.DataFrame(r.json())

    df['Close'] = df['c']
    df = df.drop('c', 1)

    df['Open'] = df['o']
    df = df.drop('o', 1)

    df['Low'] = df['l']
    df = df.drop('l', 1)

    df['High'] = df['h']
    df = df.drop('h', 1)

    df = df.drop('s', 1)

    df['timestamp'] = df['t']
    df = df.drop('t', 1)

    df['Volume'] = df['v']
    df = df.drop('v', 1)

    df['Date'] = [datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') for ts in df['timestamp']]
    df = df.drop('timestamp', 1)

    return df


def IndicatorsAddition(df):
    df = ta.utils.dropna(df)
    # Initialize Bollinger Bands Indicator
    indicator_bb = ta.volatility.BollingerBands(close=df["Close"], n=20, ndev=2)

    df['EMA'] = ta.trend.EMAIndicator(close=df['Close'], n=14, fillna=False).ema_indicator()

    df['MACD'] = ta.trend.MACD(close=df['Close'], n_slow=26, n_fast=12,
                               n_sign=9, fillna=False).macd()

    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], n=14, fillna=False).rsi()

    df['on_balance_volume'] = ta.volume.OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume'],
                                                                 fillna=False).on_balance_volume()
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df = df.drop_na()
    return df


def prepaireMARKETdata(category , pair, startDate, endDate,Long = False):
    if not  Long:
        df = prepaireCandels(category , pair, startDate, endDate)
    else:
        df = prepaireLongCandleData(category , pair, startDate, endDate)
    df = IndicatorsAddition(df)
    return df


def prepaireNews(category, pair, startDate, endDate):
    url = 'http://localhost:5000/Robonews/v1/news'
    # endDate = int(datetime.now().timestamp())
    # startDate = endDate - (SEQ_LEN_news )
    query = {'category': category,
             'keywords': pair,
             'from': startDate,
             'to': endDate
             }

    resp = requests.get(url, params=query)
    resp = json.loads(resp.text)
    df = pd.DataFrame(resp)
    return df


def data_collection_service_for_prediction(category, pair, startDate, endDate,Long = False):
    marketDF = prepaireMARKETdata(pair, startDate, endDate,Long)
    newsDF = prepaireNews(category, pair, startDate, endDate)
    return marketDF, newsDF


def marketDataTransformation(marketDf):
    marketDf = marketDf.drop("date", 1)
    marketDf = marketDf.drop("time", 1)
    marketDf = marketDf.drop("high", 1)  # don't need this anymore.
    marketDf = marketDf.drop("low", 1)  # don't need this anymore.
    marketDf = marketDf.drop("open", 1)  # don't need this anymore.

    for col in marketDf.columns:  # go through all of the columns
        if col != "target":  # normalize all ... except for the target itself!
            marketDf[col] = [float(e) for e in marketDf[col]]
            marketDf[col] = marketDf[col].pct_change()  # pct changefor  "normalizes"
            marketDf = marketDf.replace([np.inf, -np.inf], None)
            marketDf.dropna(inplace=True)  # remove the nas created by pct_change
            marketDf[col] = preprocessing.scale(marketDf[col].values)  # scale between 0 and 1.

    marketDf.dropna(inplace=True)  # cleanup again... jic.
    marketDf['target'] = marketDf['Close'].shift(-FUTURE_PERIOD_PREDICT)
    return marketDf


def modify(s):
    vec = s.replace('[', '')
    vec = vec.replace(']', '')
    vec = vec.split(',')
    vec = map(float, vec)
    vec = list(vec)
    return vec


def getNews_embedding(currentDate, df):
    df = newsDataTransformation(df, training=False)
    news_date = df.index.values
    prevDate = currentDate - timedelta(hours=SEQ_LEN_news)
    subDF = df.loc[prevDate:currentDate]
    if len(subDF) == 0:
        return (np.zeros((max_L, embedding_dim)))

    else:
        vector = np.zeros((max_L, embedding_dim))
        i = 0
        for d, row in subDF[:max_L].iterrows():
            vector[i] = np.asarray(modify(row['vector']))
            i = i + 1
        return vector


def newsDataTransformation(newsDF, training=False):
    if training == True:
        newsDF = BoEC.BoEC_word2vec()
        return newsDF
    else:
        for ele, i in zip(newsDF, range(1, len(newsDF))):
            newsDF.loc['vector', i] = BoEC.testCaseProcess(ele)
            return newsDF

def dataAlighnment(marketDF, newsDF):
    aligned_news_data = []
    sequential_data = []  # this is a list that will CONTAIN the sequences
    prev_days = deque(maxlen=SEQ_LEN)
    for d, row in marketDF.iterrows():

        prev_days.append([n for n in row[:-1]])  # store all but the target
        if len(prev_days) == SEQ_LEN:  # make sure we have 10 sequences!
            sequential_data.append(
                [np.array(prev_days), row[-1], getNews_embedding(d, newsDF), d])  # i[-1] is the sequence target

    # random.shuffle(sequential_data)  # shuffle for good measure.

    X = []
    y = []
    newsX = []
    dates = []

    for seq, target, newsEmbedding, d in sequential_data:  # going over our new sequential data
        X.append(seq)  # X is the sequences
        y.append(target)  # y is the targets/labels
        newsX.append(newsEmbedding)
        dates.append(d)

    return np.array(X), np.array(y), np.array(newsX), dates  # return X and y...and make X a numpy array!

def prepairDataForLoad(category, pair, startDate, endDate,Training = False):
    if Training:
       marketDF , newsDF =  data_collection_service_for_prediction (category, pair, startDate, endDate,Long = True)
       X_train , Y_train , news_train , dates = dataAlighnment(marketDF, newsDF)
    else:
        marketDF, newsDF = data_collection_service_for_prediction(category, pair, startDate, endDate, Long=False)
        X_train, Y_train, news_train, dates = dataAlighnment(marketDF, newsDF)




