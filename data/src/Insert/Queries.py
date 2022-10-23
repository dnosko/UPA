import json
import logging
import pymongo.database
import pymongo.errors
from glob import glob
import os
import datetime as dt
import time
from .MSG_TYPES_ENUM import MSGTYPE
from .Parser import Parser


class Queries:
    planned = 'plannedTrains'
    canceled = 'canceledTrains'
    reroute = 'rerouteTrains'

    def __init__(self, db):
        self.db = db
        try:
            self.plannedTrains = db.create_collection(self.planned)
            self.canceledTrains = db.create_collection(self.canceled)
            self.rerouteTrains = db.create_collection(self.reroute)
        except pymongo.errors.CollectionInvalid:
            self.plannedTrains = db[self.planned]
            self.canceledTrains = db[self.canceled]
            self.rerouteTrains = db[self.reroute]

    def create_indexes(self):
        self.plannedTrains.create_index([("TR.ID", pymongo.DESCENDING)])
        self.canceledTrains.create_index([("TR.ID", pymongo.DESCENDING)])
        self.rerouteTrains.create_index([("TR.ID", pymongo.DESCENDING)])

    def insert_all(self, folder: str = '../extract_data/'):
        print(os.path.exists(folder))
        for x in os.walk(folder):
            for y in glob(os.path.join(x[0], '*.xml')):
                self.insert_obj(y)

    def insert_by_cache(self, cache_path : str = "cache.json"):
        with open(cache_path, 'r') as f:
            dictionary = json.load(f)

        files = dictionary["extracted"]
        for file in files:
            if file.endswith('.xml') and os.path.isfile(file):
                self.insert_obj(file)




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
        self.plannedTrains.insert_one(obj)

    def insert_canceled(self, obj: dict):
        self.canceledTrains.insert_one(obj)

    def insert_reroute(self, obj: dict):
        self.rerouteTrains.insert_one(obj)

    def delete_all(self):
        if not self.plannedTrains.delete_many({}):
            logging.error("Error dropping plannedTrains collection!")
        if not self.rerouteTrains.delete_many({}):
            logging.error("Error dropping rerouteTrains collection!")
        if not self.canceledTrains.delete_many({}):
            logging.error("Error dropping canceledTrains collection!")

    @staticmethod
    def filter_by_time(date: dt.datetime, collection):
        return collection.find({'calendar.startDate': {'$lte': date},
                                'calendar.endDate': {'$gte': date}})

    """ Returns list of distinct names of all locations in planned trains collection """

    def select_all_locations_name(self) -> list:
        locations = self.plannedTrains.distinct('path.name', {'path.trainActivity': '0001'})

        return locations


    def create_temporary_collections(self):
        self.canceled_trains_in_date = self.db.create_collection('canceledTrainsInDate')
        self.reroute_trains_in_date = self.db.create_collection('rerouteTrainsInDate')
        self.valid_trains = self.db.create_collection('validTrains')
        self.trains_going_to_location = self.db.create_collection('goingToLocation')


    def drop_temporary_collections(self):
        self.db.drop_collection('validTrains')
        self.db.drop_collection('goingToLocation')
        self.db.drop_collection('canceledTrainsInDate')
        self.db.drop_collection('rerouteTrainsInDate')

    def find_trains(self, date: dt.datetime, from_location: str, to_location: str) -> list:
        t = time.process_time()
        self.create_temporary_collections()

        self.filter_not_valid_trains_for_date(self.canceledTrains, self.canceled_trains_in_date, date)

        self.filter_not_valid_trains_for_date(self.rerouteTrains, self.reroute_trains_in_date, date)

        self.select_valid_trains(date, 'canceledTrainsInDate', 'rerouteTrainsInDate')

        res = self.select_by_location_from_to(self.valid_trains, from_location,
                                                                  to_location)
        if res is None:
            self.drop_temporary_collections()
            return None

        formated = self.format_to_output(self.trains_going_to_location)

        self.drop_temporary_collections()
        elapsed_time = time.process_time() - t
        print(elapsed_time)
        return formated


    def filter_not_valid_trains_for_date(self, in_collection, out_collection, date: dt.datetime):
        canceled = in_collection.aggregate([
                {
                    '$addFields': {
                        'bit': {'$let': {
                            'vars': {
                                'bitIndex': {
                                    '$dateDiff': {'startDate': "$calendar.startDate", 'endDate': date, 'unit': 'day'}},
                            },
                            'in': {'$substrBytes': ['$calendar.bitmap', '$$bitIndex', 1]}
                        }}
                    }
                },
                {
                    '$match': {
                        '$and': [
                            {'calendar.startDate': {'$lte': date},
                             'calendar.endDate': {'$gte': date},
                             'bit': {'$eq': "1"}
                             }]
                    }
                },
            {'$sort': {'created': -1}},
            {'$group': {
                "_id": "$TR.ID", "latest": {
                "$first": "$$ROOT"
                } }
            },
            {
                "$replaceWith": "$latest"
            },
            {'$project': {'TRID': '$TR.ID', 'PAID': '$PA.ID', 'created': '$created'} }
        ])

        out_collection.insert_many(canceled)
        return out_collection


    def select_valid_trains(self, date: dt.datetime, canceledTrains, rerouteTrains):

        valid = self.plannedTrains.aggregate([
            {
                '$addFields': {
                    'bit': {'$let': {
                        'vars': {
                            'bitIndex': {
                                '$dateDiff': {'startDate': "$calendar.startDate", 'endDate': date, 'unit': 'day'}},
                        },
                        'in': {'$substrBytes': ['$calendar.bitmap', '$$bitIndex', 1]}
                    }}
                }
            },
            {
                '$match': {
                    '$and': [
                        {'calendar.startDate': {'$lte': date},
                         'calendar.endDate': {'$gte': date},
                         'bit': {'$eq': "1"}
                         }]
                }
            },
            {
                '$lookup': {
                    'from': canceledTrains,
                    'localField': 'TR.ID',
                    'foreignField': 'TRID',
                    'as': 'cancellations'
                }
            },
            {
                '$lookup': {
                    'from': rerouteTrains,
                    'localField': 'TR.ID',
                    'foreignField': 'TRID',
                    'as': 'reroutes'
                }

            },


            {'$match': {
                '$and': [
                   {'cancellations': {'$eq': []}},
                    {'reroutes': {'$eq': []}}
                ]
            }
            }
        ])


        self.valid_trains.insert_many(valid)



    def select_by_location_from_to(self, collection, from_location: str, to_location: str):

        filter_locations = collection.aggregate([
            {'$match': {
                '$and': [
                    {
                        'path': {'$elemMatch': {
                            'name': from_location,
                            'trainActivity': '0001'
                        }}},
                    {'path': {'$elemMatch': {
                        'name': to_location,
                        'trainActivity': '0001',
                    }}},
                ]
            }
            },
            {
                '$addFields': {
                    'isGoingTo': {'$let': {
                        'vars': {
                            'fromIndex': {'$indexOfArray': ['$path.name', from_location]},
                            'toIndex': {'$indexOfArray': ['$path.name', to_location]}
                        },
                        'in': {'$gt': ['$$toIndex', '$$fromIndex']}
                    }}
                }
            },
            {
                '$match': {
                    'isGoingTo': True,
                }
            },
        ])


        try:
            self.trains_going_to_location.insert_many(filter_locations)
            return True
        except pymongo.errors.InvalidOperation:
            logging.error('No trains found!')
            return None

    def format_to_output(self, collection) -> list:

        formated = collection.aggregate([{
            '$project': {
                'TRID': '$TR.ID',
                'PAID': '$PA.ID',
                'path': {
                    '$map': {
                        'input': {
                            '$filter': {
                                'input': '$path',
                                'as': 'location',
                                'cond': {
                                    '$in': ['0001', '$$location.trainActivity']
                                }
                            }
                        },
                        'as': 'location',
                        'in': {
                            'name': '$$location.name',
                            'arrival': '$$location.arrival',
                            'departure': '$$location.departure'
                        }
                    }
                }
            }
        }
        ])

        return list(formated)


