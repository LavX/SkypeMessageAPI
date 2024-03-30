# app.py
from flask import Flask
from endpoints.custom_messaging import custom_messaging
from endpoints.ai_messaging import ai_messaging
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FlaskApp')

app = Flask(__name__)
app.register_blueprint(custom_messaging)
app.register_blueprint(ai_messaging)


if __name__ == '__main__':
    app.run(debug=True)
