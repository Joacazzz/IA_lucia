from pymongo import MongoClient

from .config import settings


client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=10_000)
db = client[settings.MONGODB_DATABASE]


def get_db():
    yield db
