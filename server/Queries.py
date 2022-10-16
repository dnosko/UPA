import logging

import pymongo.database
from lxml import etree
from MongoDB import MongoDB

class Queries:
    planned = 'plannedTrains'
    canceled = 'canceledTrains'
    reroute = 'rerouteTrains'

    def __init__(self, db: MongoDB):
        try:
            self.plannedTrains = db.create_collection(self.planned)
            self.canceledTrains = db.create_collection(self.canceled)
            self.rerouteTrains = db.create_collection(self.reroute)
        except pymongo.errors.CollectionInvalid:
            self.plannedTrains = db[self.planned]
            self.canceledTrains = db[self.canceled]
            self.rerouteTrains = db[self.reroute]

    def insert_planned(self):
        pass

    def insert_canceled(self, identifiers: dict):
        pass

    def insert_reroute(self):
        pass

