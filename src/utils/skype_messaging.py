# skype_messaging.py
from skpy import Skype, SkypeAuthException, SkypeEventLoop, SkypeNewMessageEvent
import os
import time
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SkypeMessaging')

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, 'skype_session.skype')  # Define a session file name

# Initialize a global Skype object
global_skype = None

def get_skype_instance():
    logger.info("Getting Skype instance")
    global global_skype
    if global_skype and global_skype.conn.connected:
        return global_skype

    if os.path.exists(SESSION_FILE):
        try:
            logger.info("Loading Skype session from file")
            global_skype = Skype(tokenFile=SESSION_FILE)
            return global_skype
        except SkypeAuthException:
            logger.error("Failed to load Skype session from file")
            global_skype = None

    if global_skype is None:
        try:
            logger.info("Creating new Skype session")
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

class SkypeMessagingEventLoop(SkypeEventLoop):
    def __init__(self, skype_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skype = skype_instance
        self.received_messages = []
        logger.info("SkypeMessagingEventLoop initialized")

    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent):
            self.received_messages.append(event.msg)
            logger.info(f"Received message: {event.msg.content}")

def fetch_skype_reply(group_id, unique_id, timeout=30):
    skype = get_skype_instance()
    if skype is None:
        print("Failed to get Skype instance for fetching reply")
        logger.error("Failed to get Skype instance for fetching reply")
        return None

    skype_loop = SkypeMessagingEventLoop(skype)
    start_time = time.time()
    skype_loop.setDaemon(True)
    skype_loop.start()

    try:
        # Give some time for the message to be replied to
        while time.time() - start_time < timeout:
            logger.info("Checking for messages")
            for message in skype_loop.received_messages:
                if unique_id in message.content:
                    logger.info(f"Found reply message: {message.content}")
                    skype_loop.stop()
                    return message.content
            time.sleep(1)  # Check for messages every second
    finally:
        logger.info("Stopping Skype event loop")
        skype_loop.stop()

    logger.info("No reply message found")
    return None