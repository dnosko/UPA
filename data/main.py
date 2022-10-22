from src.Downloader.downloader import download
from src.Downloader.extract import extract_files
from src.Insert.db.MongoDB import MongoDB, MongoClient
from src.Insert.Queries import Queries

def main():
    """
    'mongodbuser'
    'your_mongodb_root_password'
    'flaskdb'
    """
    MONGO_HOST = 'localhost'
    MONGO_PORT = "27017"
    MONGO_DB = "flaskdb"
    MONGO_USER = "mongodbuser"
    MONGO_PASS = "your_mongodb_root_password"

    uri = "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB)
    print(uri)
    db = MongoClient(uri)
    queries = Queries(db.db)
    download()
    extract_files()
    #todo rewrite insert by cache file

    queries.insert_all(folder='extract_data/')





if __name__ == "__main__":
    main()