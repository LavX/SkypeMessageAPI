# custom_messaging.py
from flask import Blueprint, request, jsonify
from utils.skype_messaging import send_skype_message
from utils.api_key_manager import require_api_key


custom_messaging = Blueprint('custom_messaging', __name__)

@custom_messaging.route('/send-custom-message', methods=['POST'])
@require_api_key
def send_custom_message():
    data = request.json
    group_id = data.get('group_id')
    message = data.get('message')

    if not group_id or not message:
        return jsonify({"error": "Missing group_id or message"}), 400

    if send_skype_message(group_id, message):
        return jsonify({"success": "Message sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send message"}), 500
