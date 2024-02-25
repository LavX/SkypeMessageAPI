# app.py
from flask import Flask
from endpoints.custom_messaging import custom_messaging

app = Flask(__name__)
app.register_blueprint(custom_messaging)

if __name__ == '__main__':
    app.run(debug=False)
