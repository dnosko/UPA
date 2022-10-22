import logging
import pymongo.database
import pymongo.errors
from glob import glob
import os
import datetime as dt

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
        self.plannedTrains.create_index([("PA.ID", pymongo.DESCENDING)])
        self.canceledTrains.create_index([("TR.ID", pymongo.DESCENDING)])
        self.canceledTrains.create_index([("PA.ID", pymongo.DESCENDING)])
        self.rerouteTrains.create_index([("TR.ID", pymongo.DESCENDING)])
        self.rerouteTrains.create_index([("plannedID.ID", pymongo.DESCENDING)])

    def insert_all(self, folder: str = '../extract_data/'):
        print(os.path.exists(folder))
        for x in os.walk(folder):
            for y in glob(os.path.join(x[0], '*.xml')):
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

    def find_trains(self, date: dt.datetime, from_location: str, to_location: str) -> list:
        valid_trains_collection = self.select_valid_trains(date)
        found_trains_collection = self.select_by_location_from_to(valid_trains_collection, from_location,
                                                                  to_location)
        if found_trains_collection is None:
            return None
        formated = self.format_to_output(found_trains_collection)

        self.db.drop_collection(valid_trains_collection)
        self.db.drop_collection(found_trains_collection)
        print(len(formated))
        for i in formated:
            print(i['TRID'])
            for a in i['path']:
                print(a)

        return formated

    def select_valid_trains(self, date: dt.datetime):

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
                    'from': self.reroute,
                    "let": {"paid_r": '$plannedPAID.ID', 'trid_r': '$TR.ID', 'start': "$calendar.startDate",
                        'end': '$calendar.endDate',
                        'bitmap': '$calendar.bitmap',
                        'bitIndex': {
                            '$dateDiff': {'startDate': "$calendar.startDate", 'endDate': date, 'unit': 'day'}},
                    },
                    'pipeline': [
                        {'$match': {'$expr':
                                    {'$and': [
                                        {'$eq':
                                             ['$TR.ID', '$$trid_r']
                                         }
                                    ]}
                        }},
                        {'$match': {
                            '$expr': {
                                '$and': [
                                    {'$lte': ['$$start', date]},
                                    {'$gte': ['$$end', date]},
                                    {'$eq':
                                         [{'$substrBytes': ['$$bitmap', '$$bitIndex', 1]}, "1"]
                                     },

                                ]}
                        }},
                        {'$project': {'TRID': '$$trid_r', 'PAID': '$$paid_r'}}
                    ],
                    'as': 'reroutes'
                }
            },
            {
                '$lookup': {
                    'from': self.canceled,
                    'let': {
                        'start': "$calendar.startDate",
                        'end': '$calendar.endDate',
                        'bitmap': '$calendar.bitmap',
                        'bitIndex': {
                            '$dateDiff': {'startDate': "$calendar.startDate", 'endDate': date, 'unit': 'day'}},
                        'trid_c': '$TR.ID',
                        'paid_c': '$PA.ID'
                    },
                    'pipeline': [
                        {'$match': {
                            '$expr': {
                                '$and': [
                                    {'$lte': ['$$start', date]},
                                    {'$gte': ['$$end', date]},
                                    {'$eq':
                                         [{'$substrBytes': ['$$bitmap', '$$bitIndex', 1]}, "1"]
                                     },
                                    {'$eq':
                                         ['$TR.ID', '$$trid_c']
                                     },
                                    {'$eq':
                                         ['$PA.ID', '$$paid_c']
                                     }
                                ],
                            },
                        },
                        },
                    ],
                    'as': 'cancellations'
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

        valid_trains = self.db.create_collection('validTrains')
        valid_trains.insert_many(valid)

        return valid_trains

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
            trains_going_to_location = self.db.create_collection('goingToLocation')
            trains_going_to_location.insert_many(filter_locations)
            return trains_going_to_location
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


