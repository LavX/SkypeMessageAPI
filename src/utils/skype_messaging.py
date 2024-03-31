# skype_messaging.py
from skpy import Skype, SkypeAuthException, SkypeEventLoop, SkypeNewMessageEvent
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import json
import html
import re
import pytz
from xml.etree import ElementTree as ET
import threading
import queue




logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SkypeMessaging')

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Skype credentials and session file path
SKYPE_USERNAME = os.getenv("SKYPE_USERNAME")
SKYPE_PASSWORD = os.getenv("SKYPE_PASSWORD")
SESSION_FILE = 'skype_session.skype'

# Initialize a global Skype object
global_skype = None

message_queue = queue.Queue()


def get_skype_instance():
    global global_skype
    if global_skype and global_skype.conn.connected:
        logger.info("Skype instance is already connected.")
        return global_skype

    if os.path.exists(SESSION_FILE):
        try:
            logger.info("Loading Skype session from file.")
            global_skype = Skype(tokenFile=SESSION_FILE)  # Use the token file to authenticate
            return global_skype
        except SkypeAuthException:
            logger.error("Failed to load Skype session from file. Attempting new login.")
            global_skype = None

    if global_skype is None:
        try:
            logger.info("Creating new Skype session.")
            global_skype = Skype(os.getenv("SKYPE_USERNAME"), os.getenv("SKYPE_PASSWORD"), SESSION_FILE)
            return global_skype
        except SkypeAuthException as e:
            logger.error(f"Skype authentication failed: {e}")
            print(f"Skype authentication failed: {e}")
            return None

def message_sender():
    logger.info("Starting message sender thread...")
    while True:
        logger.info("Checking for messages to send...")
        group_id, message = message_queue.get()
        send_skype_message(group_id, message)
        time.sleep(10)
        message_queue.task_done()
        logger.info("Message sent successfully")

def enqueue_message(group_id, message):
    message_queue.put((group_id, message))
    

def send_skype_message(group_id, message):
    skype = get_skype_instance()
    if skype is None:
        logger.error("Failed to get Skype instance")
        print("Failed to get Skype instance")
        return False

    try:
        chat = skype.chats.chat(group_id)
        chat.sendMsg(message)
        logger.info("Message sent successfully")
        return True
    except Exception as e:
        logger.error(f"Error in Skype Messaging: {e}")
        print(f"Error in Skype Messaging: {e}")
        return False
    
def fetch_skype_reply(group_id, unique_id, timeout=120):
    skype = get_skype_instance()
    if skype is None:
        logger.error("Failed to get Skype instance.")
        return None

    chat = skype.chats.chat(group_id)
    # Ensure that both times are in the same timezone for accurate comparison
    start_fetch_time = datetime.now(pytz.utc)  # Assuming your server is using UTC

    while datetime.now(pytz.utc) - start_fetch_time < timedelta(seconds=timeout):
        logger.info("Checking for new messages...")
        messages = chat.getMsgs()  # Fetch the latest batch of messages
        for message in messages:
            logger.info(f"Checking message with content: {message.content}")
            logger.info(f"Checking message with time: {message.time}")
            # Convert message time to UTC for accurate comparison
            message_time_utc = message.time.replace(tzinfo=pytz.utc)
            logger.info(f"Message time in UTC: {message_time_utc}")
            logger.info(f"Start fetch time: {start_fetch_time}")
            if message_time_utc > start_fetch_time:
                parsed_message = try_parse_message(message)
                logger.info(f"Parsed message: {parsed_message}")
                if parsed_message and parsed_message.get('reply_id') == unique_id:
                    logger.info("Matching message found.")
                    return parsed_message
        
        time.sleep(1)  # Check for new messages every second

    logger.info("Timeout reached without finding a matching message.")
    return None

def try_parse_message(message):
    """Attempt to parse a Skype message's content into JSON, handling both encapsulated and HTML-encoded content."""
    try:
        # Attempt to parse the content as XML to extract the inner JSON string
        root = ET.fromstring(message.content)
        if root.text:
            json_str = html.unescape(root.text)  # Decode HTML entities
            message_json = json.loads(json_str)
            return message_json
    except ET.ParseError as e:
        # If parsing as XML fails, log the error and fall back to regex extraction
        logger.error(f"Error parsing message content as XML: {e}")
    except json.JSONDecodeError as je:
        logger.error(f"Error parsing extracted content as JSON: {je}")
    
    # Fallback method: Use regex to directly extract JSON string if XML parsing fails
    json_str_match = re.search(r'<bing-response.*?>(.*?)</bing-response>', message.content, re.DOTALL)
    if json_str_match:
        json_str = html.unescape(json_str_match.group(1))  # Decode HTML entities
        try:
            message_json = json.loads(json_str)
            return message_json
        except json.JSONDecodeError as je:
            logger.error(f"Error parsing message content as JSON: {je}")
    
    return None

threading.Thread(target=message_sender, daemon=True).start()
