from flask import Flask

def create_app():
    # A Flask app is created
    app = Flask(__name__)
    print(app.url_map)

    return app


