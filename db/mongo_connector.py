from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from local_settings import MONGO_CONFIG

# подключение к MongoDB
def get_mongo_client():
    try:
        client = MongoClient(
            MONGO_CONFIG["url"],
            serverSelectionTimeoutMS=2000
        )
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        raise