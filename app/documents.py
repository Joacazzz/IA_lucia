import datetime as dt

from pymongo import ReturnDocument

from .database import db


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def next_id(collection: str) -> int:
    counter = db.counters.find_one_and_update(
        {"_id": collection},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return counter["value"]
