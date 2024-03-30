import sqlite3
import secrets
import argparse
from functools import wraps
from flask import request, jsonify
import os
from utils.mongodb_connector import mongodb_connector
from dotenv import load_dotenv
import logging


load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('APIKeyManager')

# Define the path to the SQLite database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'db', 'api_keys.db')

# Use MongoDB if ENABLE_MONGODB is set to 'true', else use SQLite
USE_MONGODB = os.getenv('ENABLE_MONGODB', 'false').lower() == 'true'

if mongodb_connector.enabled:
    mongodb_connector.connect()
    logger.info("Using MongoDB")

# Database initialization
def init_db():
    if not USE_MONGODB:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY,
                active INTEGER NOT NULL CHECK (active IN (0,1))
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("SQLite database initialized")

# Generate a new API key
def generate_api_key():
    logger.info("API key generated")
    return secrets.token_urlsafe(32)

# Add an API key
def add_api_key():
    key = generate_api_key()
    if USE_MONGODB:
        if mongodb_connector.insert_message("api_keys", {"key": key, "active": 1}):
            return key
        else:
            logger.error("Failed to add API key, MongoDB error")
            return "Failed to add API key, MongoDB error"
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO api_keys (key, active) VALUES (?, ?)', (key, 1))
        conn.commit()
        conn.close()
        logger.info(f"SQLite API key added")
    return key

# Remove (deactivate) an API key
def remove_api_key(key):
    if USE_MONGODB:
        mongodb_connector.db.api_keys.update_one({"key": key}, {"$set": {"active": 0}})
        logger.info(f"Mongodb API key removed:")
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('UPDATE api_keys SET active = 0 WHERE key = ?', (key,))
        conn.commit()
        conn.close()
        logger.info(f"SQLite API key removed")

# Check if an API key is valid and active
def is_valid_key(key):
    if USE_MONGODB:
        result = mongodb_connector.db.api_keys.find_one({"key": key, "active": 1})
        return result is not None
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT active FROM api_keys WHERE key = ? AND active = 1', (key,))
        result = c.fetchone()
        conn.close()
        logger.info(f"API key checked")
        return result is not None

# Decorator for API protection
def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        logger.info("Checking API key")
        api_key = request.headers.get('x-api-key')
        if api_key and is_valid_key(api_key):
            logger.info("Valid API key")
            return view_function(*args, **kwargs)
        else:
            logger.error("Invalid or missing API key")
            return jsonify({"error": "Invalid or missing API key"}), 401
    logger.info("API key checked")
    return decorated_function

# CLI for managing API keys
def main():
    parser = argparse.ArgumentParser(description='API Key Manager')
    parser.add_argument('--add', action='store_true', help='Add a new API key')
    parser.add_argument('--remove', type=str, help='Remove (deactivate) an API key')
    parser.add_argument('--check', type=str, help='Check if an API key is valid and active')

    args = parser.parse_args()

    if args.add:
        key = add_api_key()
        logger.info(f"New API key generated")
        print(f'New API key: {key}')
    elif args.remove:
        remove_api_key(args.remove)
        logger.info(f"API key removed: {args.remove}")
        print(f'API key removed: {args.remove}')
    elif args.check:
        is_valid = is_valid_key(args.check)
        logger.info(f"API key checked")
        print(f'API key is {"valid" if is_valid else "invalid"}: {args.check}')



if __name__ == '__main__':
    if not USE_MONGODB:
        logger.info("Using SQLite")
        init_db()
    main()
