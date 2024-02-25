from skpy import Skype, SkypeAuthException
import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(BASE_DIR, 'skype_session.skype')  # Define a session file name

def send_skype_message(group_id, message):
    # Attempt to load an existing session.
    if os.path.exists(SESSION_FILE):
        try:
            skype = Skype(tokenFile=SESSION_FILE)
        except SkypeAuthException as e:
            print(f"Session expired or invalid: {e}")
            skype = None
    else:
        skype = None

    # If loading session failed, perform a full login.
    if skype is None:
        try:
            skype = Skype(os.getenv("SKYPE_USERNAME"), os.getenv("SKYPE_PASSWORD"), SESSION_FILE)
        except SkypeAuthException as e:
            print(f"Skype authentication failed: {e}")
            return False

    # Now we have a valid Skype object. Proceed to send the message.
    try:
        chat = skype.chats.chat(group_id)
        chat.sendMsg(message)
        return True
    except Exception as e:
        print(f"Error in Skype Messaging: {e}")
        return False