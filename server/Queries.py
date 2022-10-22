
import logging
from db.MongoDB import MongoDB
import pymongo.database
from glob import glob
from Parser import Parser
from MSG_TYPES_ENUM import MSGTYPE
import os
import datetime as dt


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

    def insert_all(self, folder: str = '../extract_data/'):
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
                    'from': self.canceled,
                    'let': {
                        'start': "$calendar.startDate",
                        'end': '$calendar.endDate',
                        'bitmap': '$calendar.bitmap',
                        'bitIndex': {'$dateDiff': {'startDate': "$calendar.startDate", 'endDate': date, 'unit': 'day'}},
                        'trid_c': '$TRID',
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
                                         ['$TRID', '$$trid_c']
                                     }
                                ],
                            },
                        },
                        },
                        {'$project': {'TRID': '$$trid_c'}}
                    ],
                    'as': 'cancellations'
                }},

            {
                '$lookup': {
                    'from': self.reroute,
                    'let': {
                        'start': "$calendar.startDate",
                        'end': '$calendar.endDate',
                        'bitmap': '$calendar.bitmap',
                        'bitIndex': {'$dateDiff': {'startDate': "$calendar.startDate", 'endDate': date, 'unit': 'day'}},
                        'trid_r': '$TRID'
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
                                         ['$TRID', '$$trid_r']
                                    }
                                ]}
                        },
                        },
                        {'$project': {'bitmap': "$$bitmap", 'start': '$$start', 'end': '$$end', 'index': '$$bitIndex'}}
                    ],
                    'as': 'reroutes'
                }
            },

            {'$match': {"reroutes": {'$eq': []}}},
            {'$match': {"cancellations": {'$eq': []}}},
        ])

        self.valid_trains = self.db.create_collection('validTrains')
        self.valid_trains.insert_many(valid)

        return valid

    def select_by_location_from_to(self, from_location: str, to_location: str):
        if from_location is None or to_location is None:
            logging.error('Location must be specified')
            return

        filter_locations = self.valid_trains.aggregate([
            {'$match': {
                    '$and': [
                        {
                            'path': { '$elemMatch': {
                            'name': from_location,
                            'trainActivity': '0001',
                        }}},
                        { 'path': {'$elemMatch': {
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

        return filter_locations

    def select_all_locations_name(self) -> list:
        locations = self.plannedTrains.distinct('path.name', {'path.trainActivity': '0001'})

        return locations

if __name__ == "__main__":
    mongo = MongoDB('test')
    q = Queries(mongo.db)
    mongo.db.drop_collection('validTrains')
    #q.select_valid_trains(dt.datetime(2022, 10, 1))
    #q.select_by_location_from_to( 'Břeclav', 'Valtice město')
    q.select_all_locations_name()
    # q.delete_all()
    # q.insert_all()


