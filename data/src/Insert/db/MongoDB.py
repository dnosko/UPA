import pymongo.collection
from pymongo import MongoClient
import logging

CONNECTION_STRING = "mongodb://localhost:27017/"

class MongoDB:
    def __init__(self, database: str):
        client = MongoClient(CONNECTION_STRING)
        self.db = client[database]

    def create_collection(self, name: str):
        return self.db.create_collection(name)

    @staticmethod
    def delete_collection(f: pymongo.collection.Collection):
        f.delete_many({})

    def test_database(self):
        test_collection = self.create_collection('testdb')
        post1 = {"_id": 0, "name": "Dasa"}
        post2 = {"_id": 1, "name": "Marek"}
        post3 = {"_id": 2, "name": "Martin"}

        test_collection.insert_many([post1, post2, post3])
        found = test_collection.find()
        if len(list(found)) != 3:
            logging.info("Data not inserted")
        test_collection.delete_many({})
        if len(list(found)) != 0:
            logging.info("Data not deleted")
        self.db.test_collection.drop()

