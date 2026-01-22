from datetime import datetime
from typing import Dict, List
from local_settings import MONGO_CONFIG
from pymongo.errors import PyMongoError
from db.mongo_connector import get_mongo_client


# запись поисковых запросов
def log_search_query(search_type: str, params: Dict, results_count: int):
    client = get_mongo_client()
    try:
        db = client[MONGO_CONFIG["database"]]
        collection = db[MONGO_CONFIG["collection"]]

        if search_type == "keyword":

            query_text = params.get("keyword") or "Все фильмы"
        else:

            genre = params.get("genre") or "Все жанры"
            y_from = params.get("from")
            y_to = params.get("to")
            query_text = f"{genre} ({y_from}-{y_to})"

        document = {
            "timestamp": datetime.now(),
            "search_type": search_type,
            "query_display": query_text,
            "params": params,
            "results_count": results_count
        }
        collection.insert_one(document)
    except PyMongoError as e:
        print(f"Ошибка записи лога в MongoDB: {e}")
    finally:
        client.close()


# топ популярных запросов
def get_top_queries(limit: int = 5) -> List[Dict]:
    client = get_mongo_client()
    try:
        db = client[MONGO_CONFIG["database"]]
        collection = db[MONGO_CONFIG["collection"]]
        pipeline = [
            {"$group": {
                "_id": {"text": "$query_display", "type": "$search_type"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "title": "$_id.text",
                "type": "$_id.type",
                "count": 1
            }}
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        print(f"Mongo Top Error: {e}")
        return []
    finally:
        client.close()


# последние 5 уникальных поисков
def get_last_unique_queries(limit: int = 5) -> List[Dict]:
    client = get_mongo_client()
    try:
        db = client[MONGO_CONFIG["database"]]
        collection = db[MONGO_CONFIG["collection"]]
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$query_display",
                "timestamp": {"$first": "$timestamp"},
                "type": {"$first": "$search_type"},
                "results_count": {"$first": "$results_count"}
            }},
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "title": "$_id",
                "type": 1,
                "timestamp": 1,
                "results_count": 1
            }}
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        print(f"Mongo Recent Error: {e}")
        return []
    finally:
        client.close()
