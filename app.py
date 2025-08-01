import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///streams.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Stream configuration
app.config["HLS_OUTPUT_DIR"] = os.path.join(os.getcwd(), "static", "streams", "hls")
app.config["DASH_OUTPUT_DIR"] = os.path.join(os.getcwd(), "static", "streams", "dash")
app.config["RECORDINGS_DIR"] = os.path.join(os.getcwd(), "static", "recordings")

# Create directories if they don't exist
os.makedirs(app.config["HLS_OUTPUT_DIR"], exist_ok=True)
os.makedirs(app.config["DASH_OUTPUT_DIR"], exist_ok=True)
os.makedirs(app.config["RECORDINGS_DIR"], exist_ok=True)

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models and routes
    import models
    import routes
    
    db.create_all()
