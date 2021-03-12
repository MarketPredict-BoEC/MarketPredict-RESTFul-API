from dotenv import load_dotenv
import os
from pymongo import MongoClient
import logging as log
import pymongo
import json
from datetime import datetime
load_dotenv("../.env", verbose=True)



class NewsModel:

    def __init__(self, ):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        database_URL = os.environ.get("DATABASE_URL")
        self.client = MongoClient(database_URL)  # When only Mongo DB is running on Docker.
        # self.client = MongoClient(
        #    "mongodb://mymongo_1:27017/")  # When both Mongo and This application is running on
        # Docker and we are using Docker Compose

        database = os.environ.get("DATABASE_NAME")
        collection = os.environ.get("ECONOMICNEWS")
        cursor = self.client[database]
        self.collection = cursor[collection]

    def read(self):
        log.info('Reading All Data')
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def save_to_DB(self, data):
        log.info('Writing Data to DB')
        try:
            response = self.collection.insert_one(data)
            return response.inserted_id

        except:

            log.info('DataBase Error')
            return False

    def validatData(self, data):
        #data = json.loads(data)
        start = data["pubDate"]
        if type(start) != type(0):
            raise TypeError("Invalid data type for pubDate!")
        elif start < 0:
            raise ValueError("Invalid Unix UTC Timestamp")
        else:
            current = datetime.now().timestamp()
            data['createdat'] = int(current)
            return data
        return False

    def find_by_Link(self, link):
        query = {'link': link}
        mydoc = self.collection.find(query)
        exist = len(list(mydoc))
        return exist

    '''
    @staticmethod
    def create_index():
        database_URL = os.environ.get("DATABASE_URL")
        myclient = MongoClient(database_URL)  # When only Mongo DB is running on Docker.
        # self.client = MongoClient(
        #    "mongodb://mymongo_1:27017/")  # When both Mongo and This application is running on
        # Docker and we are using Docker Compose

        database = os.environ.get("DATABASE_NAME")
        collection = os.environ.get("ECONOMICNEWS")
        cursor = myclient.client[database]
        myclient.collection = cursor[collection]

        myclient.collection.create_index([('category', 1), ('keywords', 1), ('pubDate', 1)])
        print(myclient.collection.index_information())
        myclient.collection.drop_indexes()
        print(myclient.collection.index_information())

    '''

    def find_by_date_keyword_category(self, keywords, start, end, category):

        log.info('find news with particular publishing timestamp and keywords')

        self.collection.create_index([('pubDate', pymongo.ASCENDING),
                                      ('category', pymongo.ASCENDING),
                                      ('keywords', pymongo.ASCENDING)],
                                     name='pubDate_category_keywords')
        log.info(self.collection.index_information())
        # queryString = {"pubDate": {"$gt": start, "$lt": end}, "keywords": "/"'.*' + keywords + '.*/"'}
        queryString = {"pubDate": {"$gt": start, "$lt": end}, "keywords": {"$in": [keywords]}, "category": category}
        documents = self.collection.find(queryString)
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        self.collection.drop_indexes()
        return output

    def find_by_keywords(self, keyword):
        log.info('find news with particular keywords')
        matchstring = {"keywords": "/"'.*' + keyword + '.*/"'}
        documents = self.collection.find(matchstring)
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def find_by_date(self, start, end):
        log.info('find news with particular publishing timestamp')
        queryString = {"pubDate": {"$gt": start, "$lt": end}}
        documents = self.collection.find(queryString)
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output
