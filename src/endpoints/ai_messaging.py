# ai_messaging.py
import os
import uuid
from flask import Blueprint, request, jsonify
from utils.skype_messaging import send_skype_message, fetch_skype_reply
from utils.api_key_manager import require_api_key
from utils.mongodb_connector import mongodb_connector
import time
import logging

ai_messaging = Blueprint('ai_messaging', __name__)

GROUP_ID = os.getenv('GROUP_ID')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AIMessaging')


def log_message_to_mongodb(timestamp, session_id, message_id, message, reply=None):
    document = {
        "timestamp": timestamp, 
        "session_id": session_id,
        "message_id": message_id,
        "message": message,
        "reply": reply
    }
    logger.info(f"logger message to MongoDB: {document}")
    try:
        mongodb_connector.insert_message("messages", document)
    except Exception as e:
        logger.error(f"Failed to log message to MongoDB: {e}")


def read_file_content(filename):
    """Utility function to read content from a file."""
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

@ai_messaging.route('/send-ai-message', methods=['POST'])
@require_api_key
def send_fixed_message():
    logger.info("Received request to send AI message")
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    

    if not user_message or not session_id:
        logger.error("Missing message or chat_id")
        return jsonify({"error": "Missing message or chat_id"}), 400

    #Get the current timestamp
    timestamp = int(time.time())

    # Reading content from files
    try:
        prompt = read_file_content('prompt.txt')
        instructions = read_file_content('instructions.txt')
    except Exception as e:
        logger.error(f"Failed to read content from files: {e}")
        return jsonify({"message": "Failed to read content from files"}), 500

    unique_id = str(uuid.uuid4())
    formatted_message = f"{prompt}\n{instructions}\nid: {unique_id}\nsession_id: {session_id}\nmessage: {user_message}"
    if os.getenv('ENABLE_MONGODB', 'false').lower() == 'true':
        logger.info(f"Logging message to MongoDB: {formatted_message}")
        try:
            log_message_to_mongodb(timestamp, session_id, unique_id, user_message)
        except Exception as e:
            logger.error(f"Failed to log message to MongoDB: {e}")

    # Sending the formatted message
    if not send_skype_message(GROUP_ID, formatted_message):
        logger.error("Failed to send message")
        return jsonify({"message": "Failed to send message"}), 500

    # Attempting to fetch the reply
    reply = fetch_skype_reply(GROUP_ID, unique_id)
    if reply:
        if reply and os.getenv('ENABLE_MONGODB', 'false').lower() == 'true':
            logger.info(f"Logging reply to MongoDB: {reply}")
            try:
                log_message_to_mongodb(timestamp, session_id, unique_id, reply=reply)
            except Exception as e: 
                logger.error(f"Failed to log reply to MongoDB: {e}")
            return jsonify({"message": reply}), 200
    else:
        logger.error("Timeout. Try again or contact administrator")
        return jsonify({"message": "Timeout. Try again or contact administrator"}), 500
