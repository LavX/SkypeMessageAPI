# custom_messaging.py
from flask import Blueprint, request, jsonify
from utils.skype_messaging import send_skype_message
from utils.api_key_manager import require_api_key
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CustomMessaging')

custom_messaging = Blueprint('custom_messaging', __name__)

@custom_messaging.route('/send-custom-message', methods=['POST'])
@require_api_key
def send_custom_message():
    logger.info("Received request to send custom message")
    data = request.json
    group_id = data.get('group_id')
    message = data.get('message')

    if not group_id or not message:
        logger.error("Missing group_id or message")
        return jsonify({"error": "Missing group_id or message"}), 400

    if send_skype_message(group_id, message):
        logger.info("Message sent successfully")
        return jsonify({"success": "Message sent successfully"}), 200
    else:
        logger.error("Failed to send message")
        return jsonify({"error": "Failed to send message"}), 500
