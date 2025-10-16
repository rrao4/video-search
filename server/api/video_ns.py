from flask_restx import Namespace, Resource, fields
from flask import jsonify
from extensions import db
from db.models import Video, Property, PropertyValue, VideoPropertyValue
from api.api_models import video_model, video_input_model
from datetime import datetime
from sqlalchemy.orm import joinedload

# Create a Namespace for videos
video_ns = Namespace("videos", description="Video related operations")

# Define the Video API
@video_ns.route("")
class VideoListAPI(Resource):
    @video_ns.marshal_with(video_model, as_list=True)
    def get(self):
        """
        Get all videos
        """
        from sqlalchemy.orm import joinedload

        videos = Video.query.options(
            joinedload(Video.video_property_values)  # load the join table
            .joinedload(VideoPropertyValue.property_value)  # load the PropertyValue
            .joinedload(PropertyValue.property)  # load the Property
            .joinedload(Property.parent),  # load the immediate parent
            joinedload(Video.descriptions)  # also load descriptions
        ).all()
        return [video.to_dict() for video in videos], 200

    @video_ns.expect(video_input_model)
    @video_ns.marshal_with(video_model)
    def post(self):
        """
        Create a new video
        """
        data = video_ns.payload

        existing_video = Video.query.filter_by(path=data["path"]).first()
        if existing_video:
            return jsonify({"error": "video path already exists"}), 400
        
        
        new_video = Video(
            path=data["path"],
            aspect_ratio=data.get("aspect_ratio"),
            genre=data.get("genre")
        )
        db.session.add(new_video)
        db.session.commit()
        return new_video.to_dict(), 201

@video_ns.route("/<string:query>")
class VideoAPI(Resource):
    @video_ns.marshal_with(video_model)
    def get(self, query):
        if query == "" or query is None:
            videos = Video.query.all()
        else:   
            videos = Video.query.filter_by(genre=query).all()

        return [video.to_dict() for video in videos], 200

@video_ns.route("/<int:id>")
class VideoByIdAPI(Resource):
    @video_ns.marshal_with(video_model)
    def get(self, id):
        """
        Get a video by ID
        """
        video = Video.query.options(
            joinedload(Video.video_property_values)
            .joinedload(VideoPropertyValue.property_value)
            .joinedload(PropertyValue.property)
            .joinedload(Property.parent),
            joinedload(Video.descriptions)
        ).get(id)
        
        if not video:
            return {"error": "Video not found"}, 404
        return video.to_dict(), 200

    @video_ns.expect(video_input_model)
    @video_ns.marshal_with(video_model)
    def put(self, id):
        """
        Update a video by ID
        """
        data = video_ns.payload
        video = Video.query.get(id)
        if not video:
            return jsonify({"error": "Video not found"}), 404
        video.path=data["path"]
        video.aspect_ratio=data.get("aspect_ratio")
        video.genre=data.get("genre")
        db.session.commit()
        return video.to_dict(), 200

    def delete(self, id):
        """
        Delete a video by ID
        """
        video = Video.query.get(id)
        if not video:
            return jsonify({"error": "Video not found"}), 404
        db.session.delete(video)
        db.session.commit()
        return jsonify({"message": "Video deleted"}), 200
    
# @video_ns.route("/<int:id>")
# class VideoAPI(Resource):
#     @video_ns.marshal_with(video_model)
#     def get(self, id):
#         """
#         Get a video by ID
#         """
#         video = Video.query.get(id)
#         if not video:
#             return jsonify({"error": "Video not found"}), 404
#         return video.to_dict(), 200