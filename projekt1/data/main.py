from src.Downloader.downloader import download
from src.Downloader.extract import extract_files,extract_files_from_caches
from src.Insert.db.MongoDB import MongoDB, MongoClient
from src.Insert.Queries import Queries
from config import CACHE_INSERT
def main():

    MONGO_HOST = 'localhost'
    MONGO_PORT = "27017"
    MONGO_DB = "flaskdb"
    MONGO_USER = "mongodbuser"
    MONGO_PASS = "your_mongodb_root_password"

    uri = "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB)

    db = MongoClient(uri)
    queries = Queries(db.db)
    download()
    extract_files_from_caches()

    if CACHE_INSERT:
        queries.insert_by_cache()
    else:
        queries.insert_all()


if __name__ == "__main__":
    main()