from datetime import datetime
import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS, cross_origin


from src.Queries import Queries

application = Flask(__name__)
cors = CORS(application)
application.config["CORS_HEADERS"] = "Content-Type"


MONGO_HOST = 'mongodb'
MONGO_PORT = "27017"
MONGO_DB = "flaskdb"
MONGO_USER = "mongodbuser"
MONGO_PASS = "your_mongodb_root_password"

uri = "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB)

db = MongoClient(uri)
queries = Queries(db.db)

@application.route('/',)
@cross_origin()
def index():
    return jsonify(message='Hello world ')


@application.route('/locations')
@cross_origin()
def locations():
    return jsonify(locations=queries.select_all_locations_name())

@application.route('/path', methods=['GET','POST'])
@cross_origin()
def createTodo():
    #date = request.args.get('date')
    #from_location = request.args.get('from')
    #to_location = request.args.get('to')
    data = request.get_json()
    date = data['date']
    from_location= data['from']
    to_location = data['to']
    date_object = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return jsonify(paths=list(queries.find_trains(date_object, from_location, to_location)))






if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5001)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
