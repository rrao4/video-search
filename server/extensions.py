from flask_sqlalchemy import SQLAlchemy 
from flask_restx import Api
from flask_cors import CORS

api = Api()
db = SQLAlchemy()
cors = CORS()