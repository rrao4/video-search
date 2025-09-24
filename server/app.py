from flask import Flask 
import os
from dotenv import load_dotenv
from extensions import api, db, cors
#from api.resources import ns
from api.auth_ns import auth
from api.video_ns import video_ns
from api.collection_ns import collection_ns
from api.property_ns import property_ns
from api.property_value_ns import property_value_ns
from api.video_embedding_ns import video_embedding_ns
from api.video_description_ns import video_description_ns
from api.video_property_value_ns import video_property_value_ns

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    api.init_app(app)
    db.init_app(app)
    cors.init_app(app, origins='*')
    #api.add_namespace(ns)
    api.add_namespace(auth)
    api.add_namespace(video_ns)
    api.add_namespace(collection_ns)
    api.add_namespace(property_ns)
    api.add_namespace(property_value_ns)
    api.add_namespace(video_embedding_ns)
    api.add_namespace(video_description_ns)
    api.add_namespace(video_property_value_ns)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
