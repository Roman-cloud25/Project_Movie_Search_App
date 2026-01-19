from datetime import datetime
from typing import Dict
from local_settings import MONGO_CONFIG
from pymongo.errors import PyMongoError
from db.mongo_connector import get_mongo_client


# запись поисковых запросов
def log_search_query(search_type: str, params: Dict, results_count: int):
    client = get_mongo_client()
    try:
        db = client[MONGO_CONFIG["database"]]
        collection = db[MONGO_CONFIG["collection"]]
        document = {
            "timestamp": datetime.now(),
            "search_type": search_type,
            "params": params,
            "results_count": results_count
        }
        collection.insert_one(document)
    except PyMongoError as e:
        print(f"Ошибка записи лога в MongoDB: {e}")
    finally:
        client.close()


# подсчет популярные, недавние
def get_top_queries(limit: int = 5):
    client = get_mongo_client()
    try:
        db = client[MONGO_CONFIG["database"]]
        collection = db[MONGO_CONFIG["collection"]]
        pipeline = [
            {"$group": {
                "_id": {"search_type": "$search_type", "params": "$params"},
                "count": {"$sum": 1},
                "avg_results": {"$avg": "$results_count"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return list(collection.aggregate(pipeline))
    finally:
        client.close()


# история последних 5 поисков
def get_last_unique_queries(limit: int = 5):
    client = get_mongo_client()
    try:
        db = client[MONGO_CONFIG["database"]]
        collection = db[MONGO_CONFIG["collection"]]
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": {"search_type": "$search_type", "params": "$params"},
                "timestamp": {"$first": "$timestamp"},
                "results_count": {"$first": "$results_count"},
                "search_type": {"$first": "$search_type"},
                "params": {"$first": "$params"}
            }},
            {"$sort": {"timestamp": -1}},
            {"$limit": limit}
        ]
        return list(collection.aggregate(pipeline))
    finally:
        client.close()
