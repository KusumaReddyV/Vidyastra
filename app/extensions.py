import logging

from flask_login import LoginManager
from pymongo import MongoClient


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"

mongo_client = None
mongo_db = None


def init_mongo(app):
    """Initialize MongoDB client using app configuration."""
    global mongo_client, mongo_db
    try:
        mongo_client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=2000)
        mongo_client.admin.command("ping")
        mongo_db = mongo_client[app.config["MONGO_DB_NAME"]]
    except Exception as exc:
        logging.warning("MongoDB not available, running with limited mode: %s", exc)
        mongo_client = None
        mongo_db = None
    return mongo_db
