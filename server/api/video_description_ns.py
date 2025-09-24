from flask import request
from flask_restx import Resource, Namespace, fields
from extensions import db
from db.models import VideoDescription, Video
from api.api_models import video_description_model, video_description_input_model

video_description_ns = Namespace("video-descriptions", description="Video description operations")

# =====================================================
# VideoDescription Endpoints
# =====================================================
@video_description_ns.route("")
class VideoDescriptionListAPI(Resource):

    @video_description_ns.marshal_list_with(video_description_model)
    def get(self):
        """List all video descriptions"""
        return VideoDescription.query.all()

    @video_description_ns.expect(video_description_input_model)
    @video_description_ns.marshal_with(video_description_model, code=201)
    def post(self):
        """Create a new video description"""
        data = video_description_ns.payload

        # Optional: check if video exists
        if not Video.query.get(data["video_id"]):
            video_description_ns.abort(400, "Video ID does not exist")

        vd = VideoDescription(
            video_id=data["video_id"],
            description=data["description"]
        )
        db.session.add(vd)
        db.session.commit()
        return vd


@video_description_ns.route("/<int:description_id>")
@video_description_ns.response(404, "VideoDescription not found")
class VideoDescriptionAPI(Resource):

    @video_description_ns.marshal_with(video_description_model)
    def get(self, description_id):
        """Get a video description by ID"""
        vd = VideoDescription.query.get(description_id)
        if not vd:
            video_description_ns.abort(404, "VideoDescription not found")
        return vd

    def delete(self, description_id):
        """Delete a video description by ID"""
        vd = VideoDescription.query.get(description_id)
        if not vd:
            video_description_ns.abort(404, "VideoDescription not found")
        db.session.delete(vd)
        db.session.commit()
        return {"message": "VideoDescription deleted successfully"}, 200
