from pymongo import MongoClient
from bson import ObjectId
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://backupkasyap_db_user:iRAQle4sNlbQrVWA@nyayaai.pgktydp.mongodb.net/?appName=nyayaai")
MONGODB_DB  = os.getenv("MONGODB_DB", "nyayaai")

client = MongoClient(MONGODB_URL)
db = client[MONGODB_DB]
blogs_collection = db.blogs