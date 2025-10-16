from flask import Flask, send_from_directory 
import os
from dotenv import load_dotenv
from extensions import api, db, cors, login_manager
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
    cors.init_app(app, origins='*') # TODO: update this later on to the frontend origin
    # login_manager.init_app(app)

    #api.add_namespace(ns)
    api.add_namespace(auth)
    api.add_namespace(video_ns)
    api.add_namespace(collection_ns)
    api.add_namespace(property_ns)
    api.add_namespace(property_value_ns)
    api.add_namespace(video_embedding_ns)
    api.add_namespace(video_description_ns)
    api.add_namespace(video_property_value_ns)

    # Static file routes for WebP videos
    # TODO: once we store the WebP's in cloud, remove this route and serve directly with cloud URLs
    @app.route('/static/webp/<filename>')
    def serve_webp(filename):
        """Serve WebP files from the video_pipeline/webp_output directory"""
        webp_dir = os.path.join(os.path.dirname(__file__), 'video_pipeline', 'webp_output')
        return send_from_directory(webp_dir, filename)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
