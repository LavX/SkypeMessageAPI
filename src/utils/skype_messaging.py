# skype_messaging.py
from skpy import Skype, SkypeAuthException, SkypeEventLoop, SkypeNewMessageEvent
import os
import time
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, 'skype_session.skype')  # Define a session file name

# Initialize a global Skype object
global_skype = None

def get_skype_instance():
    global global_skype
    if global_skype and global_skype.conn.connected:
        return global_skype

    if os.path.exists(SESSION_FILE):
        try:
            global_skype = Skype(tokenFile=SESSION_FILE)
            return global_skype
        except SkypeAuthException:
            global_skype = None

    if global_skype is None:
        try:
            global_skype = Skype(os.getenv("SKYPE_USERNAME"), os.getenv("SKYPE_PASSWORD"), SESSION_FILE)
            return global_skype
        except SkypeAuthException as e:
            print(f"Skype authentication failed: {e}")
            return None

def send_skype_message(group_id, message):
    skype = get_skype_instance()
    if skype is None:
        print("Failed to get Skype instance")
        return False

    try:
        chat = skype.chats.chat(group_id)
        chat.sendMsg(message)
        return True
    except Exception as e:
        print(f"Error in Skype Messaging: {e}")
        return False

class SkypeMessagingEventLoop(SkypeEventLoop):
    def __init__(self, skype_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skype = skype_instance
        self.received_messages = []

    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent):
            self.received_messages.append(event.msg)

def fetch_skype_reply(group_id, unique_id, timeout=30):
    skype = get_skype_instance()
    if skype is None:
        print("Failed to get Skype instance for fetching reply")
        return None

    skype_loop = SkypeMessagingEventLoop(skype)
    start_time = time.time()
    skype_loop.setDaemon(True)
    skype_loop.start()

    try:
        # Give some time for the message to be replied to
        while time.time() - start_time < timeout:
            for message in skype_loop.received_messages:
                if unique_id in message.content:
                    skype_loop.stop()
                    return message.content
            time.sleep(1)  # Check for messages every second
    finally:
        skype_loop.stop()

    return None