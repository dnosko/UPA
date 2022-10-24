import json
import logging
import pymongo.database
import pymongo.errors
from glob import glob
import os
import datetime as dt
import time



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


    @staticmethod
    def insert(collection, obj: dict):
        collection.replace_one({'TR': obj['TR'], 'PA': obj['PA']},obj, upsert=True)

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
        try:
            self.db.drop_collection('validTrains')
            self.db.drop_collection('goingToLocation')
            self.db.drop_collection('canceledTrainsInDate')
            self.db.drop_collection('rerouteTrainsInDate')
        except pymongo.errors.CollectionInvalid:
            return

    def find_trains(self, date: dt.datetime, from_location: str, to_location: str) -> list:
        t = time.process_time()
        self.drop_temporary_collections()
        self.create_temporary_collections()
        try:
            self.filter_not_valid_trains_for_date(self.canceledTrains, self.canceled_trains_in_date, date)

            self.filter_not_valid_trains_for_date(self.rerouteTrains, self.reroute_trains_in_date, date)

            self.select_valid_trains(date, 'canceledTrainsInDate', 'rerouteTrainsInDate')

            res = self.select_by_location_from_to(self.valid_trains, from_location,
                                                                      to_location)
        except pymongo.errors.InvalidOperation:
            self.drop_temporary_collections()
            return []

        if res is None:
            self.drop_temporary_collections()
            return []


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
                            'arrival': {'$dateToString': { 'format': "%H:%M:%S", 'date': "$$location.arrival" }},
                            'departure': {'$dateToString': { 'format': "%H:%M:%S", 'date': "$$location.departure" }},
                        }
                    }
                }
            }
        }
        ])

        return list(formated)


