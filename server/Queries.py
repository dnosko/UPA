import logging

import pymongo.database
from glob import glob
from MongoDB import MongoDB
from Parser import  Parser
from MSG_TYPES_ENUM import MSGTYPE
import os

class Queries:
    planned = 'plannedTrains'
    canceled = 'canceledTrains'
    reroute = 'rerouteTrains'


    def __init__(self, db):
        try:
            self.plannedTrains = db.create_collection(self.planned)
            self.canceledTrains = db.create_collection(self.canceled)
            self.rerouteTrains = db.create_collection(self.reroute)
        except pymongo.errors.CollectionInvalid:
            self.plannedTrains = db[self.planned]
            self.canceledTrains = db[self.canceled]
            self.rerouteTrains = db[self.reroute]

    def insert_all(self, folder: str = '../extract_data/'):
        for x in os.walk(folder):
            for y in glob(os.path.join(x[0], '*.xml')):
                #print(y)
                self.insert_obj(y)

    def insert_obj(self, file: str):
        parser = Parser()
        parsed_obj = parser.parse_file(file)
        if parser.msg_type == MSGTYPE.PLANNED:
            self.insert_planned(parsed_obj)
        elif parser.msg_type == MSGTYPE.CANCELED:
            self.insert_canceled(parsed_obj)
        elif parser.msg_type == MSGTYPE.REROUTE:
            self.insert_reroute(parsed_obj)


    def insert_planned(self, obj: dict):
        self.plannedTrains.collection.insert_one(obj)

    def insert_canceled(self, obj: dict):
        self.canceledTrains.collection.insert_one(obj)

    def insert_reroute(self, obj: dict):
        self.rerouteTrains.collection.insert_one(obj)

    def delete_all(self):
        if not self.plannedTrains.collection.delete_many({}):
            logging.error("Error dropping plannedTrains collection!")
        if not self.rerouteTrains.collection.delete_many({}):
            logging.error("Error dropping rerouteTrains collection!")
        if not self.canceledTrains.collection.delete_many({}):
            logging.error("Error dropping canceledTrains collection!")

if __name__ == "__main__":
    mongo = MongoDB('test')
    q = Queries(mongo.db)
    q.delete_all()
    q.insert_all()