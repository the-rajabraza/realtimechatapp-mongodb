import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Use environment variable if available, otherwise use the hardcoded URI
MONGODB_URI = os.environ.get('MONGODB_URI', "YOUR-CONNECTION-STRING")

def get_database():
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
    # Explicitly specify the database name
    return client['realchat']

def ping_database():
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)