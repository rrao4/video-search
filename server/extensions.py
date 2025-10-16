from flask_sqlalchemy import SQLAlchemy 
from flask_restx import Api
from flask_cors import CORS
from flask_login import LoginManager

api = Api()
db = SQLAlchemy()
cors = CORS()
login_manager = LoginManager()