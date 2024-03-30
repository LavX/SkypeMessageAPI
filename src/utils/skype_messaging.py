# skype_messaging.py
from skpy import Skype, SkypeAuthException, SkypeEventLoop, SkypeNewMessageEvent
import os
import time
from dotenv import load_dotenv
import logging
import json
import html
import re


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
    
class SimpleSkypeEventLoop(SkypeEventLoop):
    def __init__(self):
        # Initialize the SkypeEventLoop with the username, password, and token file
        super().__init__(SKYPE_USERNAME, SKYPE_PASSWORD, SESSION_FILE)
        self.received_messages = []

    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent):
            logger.info(f"New message received: {event.msg.content}")
            self.received_messages.append(event.msg)


def fetch_skype_reply(group_id, unique_id, timeout=30):
    event_loop = SimpleSkypeEventLoop()
    start_time = time.time()
    found_message_json = None

    logger.info(f"Listening for replies in group {group_id} with unique_id: {unique_id}")
    while time.time() - start_time < timeout and found_message_json is None:
        event_loop.cycle()  # Process any pending events
        for message in event_loop.received_messages:
            if hasattr(message, 'chat') and message.chat.id == group_id and unique_id in message.content:
                # Extract JSON string from the message content
                json_str_match = re.search(r'<code class="language-json">(.*?)</code>', message.content, re.DOTALL)
                if json_str_match:
                    json_str = json_str_match.group(1)
                    # Decode HTML entities in the JSON string
                    json_str_decoded = html.unescape(json_str)
                    try:
                        # Try to parse the decoded JSON string
                        message_json = json.loads(json_str_decoded)
                        logger.info(f"Found reply message: {json_str_decoded}")
                        found_message_json = message_json
                        break
                    except json.JSONDecodeError as e:
                        # Handle the case where json_str_decoded is not valid JSON
                        logger.error(f"Error parsing message content as JSON: {e}")
                        continue
        time.sleep(1)  # Prevent tight looping
    return found_message_json