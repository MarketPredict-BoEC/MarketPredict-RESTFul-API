from dotenv import load_dotenv
import os
from pymongo import MongoClient
import logging as log
import pandas as pd

load_dotenv("../.env", verbose=True)


class ConceptsModel:

    def __init__(self, ):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        database_URL = os.environ.get("DATABASE_URL")
        self.client = MongoClient(database_URL)  # When only Mongo DB is running on Docker.
        
        self.outputStandard = ['word', 'cluster']
        database = os.environ.get("DATABASE_NAME")
        collection = os.environ.get("CONCEPTS_COLLECTION")
        cursor = self.client[database]
        self.collection = cursor[collection]

    def read(self):
        log.info('Reading All Data')
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item in self.outputStandard} for data in documents]
        return output

    def save_to_DB(self, data):
        try:
            df = pd.DataFrame(data)
            print(df)
            print( df['pair'].iloc[0])
            query = {'pair': df['pair'].iloc[0]}
            d = self.collection.delete_many(query)
            for i, row in df.iterrows():
                node = {
                    "pair": row['pair'],
                    'word': row['word'],
                    'cluster': row['cluster']
                }
                resp = self.collection.insert_one(node)
            return True
        except Exception:
            print('Database Error')
            return False

    def find_by_pair(self, pair):
        query = {'pair': pair}
        mydoc = self.collection.find(query)
        output = [{item: data[item] for item in data if item in self.outputStandard} for data in mydoc]
        return output
