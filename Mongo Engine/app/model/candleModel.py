from dotenv import load_dotenv
import os
from pymongo import MongoClient
import logging as log
import pandas as pd
import pymongo
import numpy
import json
from datetime import datetime

load_dotenv("../.env", verbose=True)


class CandleModel:

    def __init__(self, ):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        database_URL = os.environ.get("DATABASE_URL")
        self.client = MongoClient(database_URL)  # When only Mongo DB is running on Docker.
       
        self.standardOutput = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        database = os.environ.get("DATABASE_NAME")
        collection = os.environ.get("CANDLE_COLLECTION")
        cursor = self.client[database]
        self.collection = cursor[collection]

    def save_one_DB(self, data, symbol, resolution):
        try:
            log.info('Writing Data to DB')
            data['symbol'] = symbol
            data['resolution'] = resolution
            data['timestamp'] = int(data['timestamp'])
            print(data)
            response = self.collection.insert_one(data)
            return response.inserted_id

        except Exception:
            print('DataBase Error')
            return False

    def validatData(self, symbol, resolution, start=0, end=0):

        symbols = ['DXY', 'XAUUSD', 'EURUSD',
                   'USDJPY', 'NI225',
                   'UKOIL', 'NDX', 'CHFUSD']
        resolutions = {
            'minutes': '1',
            'hour': 'H',
            '4Hour': '4H',
            'day': 'D',
        }
        if symbol.upper() not in symbols:
            raise ValueError('Invalid symbol')
        elif str(resolution) not in list( resolutions.values()):
            raise ValueError('Invalid resolution')
        elif start > end:
            raise ValueError('Invalid timestamp')

        else:
            return True

    def save_many_DB(self, data):

        log.info('Writing Data to DB')
        candles = pd.DataFrame(data['candles'])

        symbol = data['symbol']
        resolution = data['resolution']
        try:
            for i, row in candles.iterrows():
                if not self.checkForExist(symbol, resolution, row['timestamp']):
                    resp = self.save_one_DB(row, symbol, resolution)
                    if not resp:
                        raise ConnectionError

            return True
        except Exception:
            log.info('DataBase Error')
            return False

    # for get request symbole,resolution, from,to parameters
    def find_by_date_symbol_resolution(self, symbol, start, end, resolution):
        try:
            print(1)
            self.collection.create_index([('symbol', pymongo.ASCENDING),
                                          ('resolution', pymongo.ASCENDING),
                                          ('timestamp', pymongo.ASCENDING)],
                                         name='timestamp_resolution_symbol')
            log.info(self.collection.index_information())

            queryString = {"timestamp": {"$gte": int(start), "$lte": int(end)}, "symbol": symbol,
                           "resolution": str(resolution)}
            candles = self.collection.find(queryString)
            

            closeList = []
            openList = []
            lowList = []
            highList = []
            tsList = []
            volList = []

            for item in list(candles):
                closeList.append(item['close'])
                openList.append(item['open'])
                lowList.append(item['low'])
                highList.append(item['high'])
                tsList.append(int(item['timestamp']))
                volList.append(item['volume'])
            output = {
                'open': openList,
                'high': highList,
                'close': closeList,
                'low': lowList,
                'volume': volList,
                'timestamp': tsList
            }

            self.collection.drop_indexes()

            return output
        except Exception:
            print(Exception)
            return False

    def checkForExist(self, symbol, resolution, timestamp):
        log.info('find news with particular keywords')

        queryString = {"timestamp": timestamp, "symbol": symbol, "resolution": resolution}
        candles = self.collection.find(queryString)
        exist = len(list(candles))
        return exist

    def find_by_symbol(self, symbol):
        query = {'symbol': symbol}
        print(1)
        info = self.collection.find(query)
        output = [{item: data[item] for item in data if item in self.standardOutput} for data in info]
        return output
