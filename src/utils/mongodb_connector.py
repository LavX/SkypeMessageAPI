from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MongoDBConnector')

class MongoDBConnector:

    def __init__(self):
        self.client = None
        self.db = None
        self.enabled = os.getenv('ENABLE_MONGODB', 'false').lower() == 'true'
        if self.enabled:
            logger.info("MongoDBConnector initialized and MongoDB is enabled")
        else:
            logger.info("MongoDBConnector initialized but MongoDB is disabled")

    def connect(self):
        if not self.enabled:
            logger.info("MongoDB connection skipped because it is disabled")
            return
        db_name = os.getenv('MONGODB_DB_NAME')
        host = os.getenv('MONGODB_URI')
        user = os.getenv('MONGODB_USER', '').strip()
        password = os.getenv('MONGODB_PASSWORD', '').strip()

        if user and password:
            mongo_uri = f"mongodb://{user}:{password}@{host}/{db_name}"
        else:
            mongo_uri = f"mongodb://{host}/{db_name}"

        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")

    def insert_message(self, collection_name, document):
        if not self.db:
            logger.warning("Attempted to insert message without a MongoDB connection")
            return False
        try:
            collection = self.db[collection_name]
            collection.insert_one(document)
            logger.info(f"Successfully inserted document into {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            return False

# Create the MongoDBConnector instance
mongodb_connector = MongoDBConnector()