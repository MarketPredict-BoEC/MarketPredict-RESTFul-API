from dotenv import load_dotenv
import os
from pymongo import MongoClient
import logging as log
import pymongo
import json
from datetime import datetime
load_dotenv("../.env", verbose=True)



class PredictModel:

    def __init__(self, ):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        database_URL = os.environ.get("DATABASE_URL")
        self.client = MongoClient(database_URL)  # When only Mongo DB is running on Docker.
        # self.client = MongoClient(
        #    "mongodb://mymongo_1:27017/")  # When both Mongo and This application is running on
        # Docker and we are using Docker Compose

        database = os.environ.get("DATABASE_NAME")
        collection = os.environ.get("PREDICT_COLLECTION")
        cursor = self.client[database]
        self.collection = cursor[collection]


    def save_to_DB(self, data):
        log.info('Writing Data to DB')
        try:
            response = self.collection.insert_one(data)
            return response.inserted_id

        except:

            log.info('DataBase Error')
            return False

    def validatData(self, data):

        if data['category'] not in ["forex",'cryptocurrency']:
            raise TypeError("Invalid data type for pubDate!")
        if data['pair'] not in ["EURUSD","USDJPY","GBPUSD","BTCUSD"]:
            raise TypeError("Invalid data type for pubDate!")
        elif data['timestamp'] < 0:
            raise ValueError("Invalid Unix UTC Timestamp")
        else:
            current = datetime.now().timestamp()
            data['createdat'] = int(current)
            return data
        return False


    def find_by_date_pair_category(self, pair, timestamp, category):

        log.info('find news with particular publishing timestamp and keywords')

        self.collection.create_index([('pair', pymongo.ASCENDING),
                                      ('category', pymongo.ASCENDING),
                                      ('timestamp', pymongo.ASCENDING)],
                                     name='pubDate_category_keywords')
        log.info(self.collection.index_information())

        queryString = {"timestamp": {"$lt": timestamp}, "pair":pair , "category": category}
        prediction = self.collection.find(queryString)
        output = [{item: data[item] for item in data if item not in [ '_id','pair','category']} for data in prediction]
        self.collection.drop_indexes()
        return output[-1]

    def find_by_pair(self, pair):
        log.info('find news with particular keywords')
        matchstring = {"keywords": pair}
        prediction = self.collection.find(matchstring)
        output = [{item: data[item] for item in data if item != '_id'} for data in prediction]
        return output

