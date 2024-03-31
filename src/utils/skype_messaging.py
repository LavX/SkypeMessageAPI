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


def session_file_is_old_or_missing(file_path):
    """Check if the session file is older than 24 hours or does not exist."""
    if not os.path.exists(file_path):
        logger.info("Session file does not exist.")
        return True
    last_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    if datetime.now() - last_modified_time > timedelta(hours=24):
        logger.info("Session file is older than 24 hours.")
        return True
    return False

def create_new_skype_session():
    """Create a new Skype session and return the instance."""
    try:
        logger.info("Creating new Skype session.")
        return Skype(os.getenv("SKYPE_USERNAME"), os.getenv("SKYPE_PASSWORD"), SESSION_FILE)
    except SkypeAuthException as e:
        logger.error(f"Skype authentication failed: {e}")
        print(f"Skype authentication failed: {e}")
        return None

def get_skype_instance():
    global global_skype
    if global_skype and global_skype.conn.connected:
        logger.info("Skype instance is already connected.")
        return global_skype

    if session_file_is_old_or_missing(SESSION_FILE):
        global_skype = create_new_skype_session()
        return global_skype

    try:
        logger.info("Loading Skype session from file.")
        global_skype = Skype(tokenFile=SESSION_FILE)  # Use the token file to authenticate
        return global_skype
    except SkypeAuthException:
        logger.error("Failed to load Skype session from file. Attempting new login.")
        global_skype = create_new_skype_session()
        return global_skype

def message_sender():
    logger.info("Starting message sender thread...")
    while True:
        logger.info("Checking for messages to send...")
        group_id, message = message_queue.get()
        send_skype_message(group_id, message)
        time.sleep(30)
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
        # logger.info("Checking for new messages...")
        messages = chat.getMsgs()  # Fetch the latest batch of messages
        for message in messages:
            # logger.info(f"Checking message with time: {message.time}")
            # Convert message time to UTC for accurate comparison
            message_time_utc = message.time.replace(tzinfo=pytz.utc)
            # logger.info(f"Message time in UTC: {message_time_utc}")
            # logger.info(f"Start fetch time: {start_fetch_time}")
            if message_time_utc > start_fetch_time:
                logger.info(f"Checking message with content: {message.content}")
                parsed_message = try_parse_message(message)
                logger.info(f"Parsed message: {parsed_message}")
                if parsed_message and parsed_message.get('reply_id') == unique_id:
                    logger.info("Matching message found.")
                    return parsed_message
        
        time.sleep(1)  # Check for new messages every second

    logger.info("Timeout reached without finding a matching message.")
    return None

def clean_xml_content(content):
    """Cleans XML content by removing or replacing invalid characters."""
    # Remove characters before the first "<"
    content = re.sub(r'^[^<]+', '', content)
    # Remove characters after the last ">"
    content = re.sub(r'>[^>]+$', '>', content)
    # Wrap content in a root element if it contains multiple root elements
    try:
        ET.fromstring(content)
    except ET.ParseError:
        content = f'<root>{content}</root>'
    return content

def extract_json_from_xml(content):
    """Extracts JSON string from XML content, handling cases where the target text may be nested."""
    try:
        root = ET.fromstring(content)
        # Check if root.text is None and handle accordingly
        if root.text is not None:
            json_str = html.unescape(root.text)
        else:
            # If root.text is None, look for JSON within child elements
            # This is a simplified example; you may need to adjust based on your XML structure
            json_str = ''
            for child in root:
                if child.text:
                    json_str += html.unescape(child.text)
                # Optionally, handle nested structures or attributes if your data requires it
        return json_str
    except ET.ParseError as e:
        logger.error(f"Error parsing message content as XML: {e}")
        return None

def try_parse_message(content):
    """Attempts to parse a Skype message's content into JSON."""
    # Convert content to string if it's not already
    if not isinstance(content, str):
        content = str(content)

    content = clean_xml_content(content)

    # Attempt to directly parse the content as JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass  # Continue to try other methods if direct JSON parsing fails

    # Attempt to extract JSON from XML content
    json_str = extract_json_from_xml(content)
    if json_str:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing content as JSON: {e}")
    
    # Attempt to extract and parse JSON using regex
    json_str_match = re.search(r'<pre><code class="language-json">(.*?)</code></pre>', content, re.DOTALL)
    if json_str_match:
        json_str = html.unescape(json_str_match.group(1))
        # Remove invalid control characters
        json_str = re.sub(r'[\x00-\x1f]+', '', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing message content as JSON after regex extraction: {e}")

    return None

threading.Thread(target=message_sender, daemon=True).start()
