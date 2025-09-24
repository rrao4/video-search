from flask import request
from flask_restx import Resource, Namespace, fields
from extensions import db
from db.models import VideoEmbedding, Video
from api.api_models import video_embedding_model, video_embedding_input_model

video_embedding_ns = Namespace("video-embeddings", description="Video embedding operations")



# =====================================================
# VideoEmbedding Endpoints
# =====================================================
@video_embedding_ns.route("")
class VideoEmbeddingListAPI(Resource):

    @video_embedding_ns.marshal_list_with(video_embedding_model)
    def get(self):
        """List all video embeddings"""
        return VideoEmbedding.query.all()

    @video_embedding_ns.expect(video_embedding_input_model)
    @video_embedding_ns.marshal_with(video_embedding_model, code=201)
    def post(self):
        """Create a new video embedding"""
        data = video_embedding_ns.payload

        # Optional: check if video exists
        if not Video.query.get(data["video_id"]):
            video_embedding_ns.abort(400, "Video ID does not exist")

        ve = VideoEmbedding(
            video_id=data["video_id"],
            embedding=data["embedding"]
        )
        db.session.add(ve)
        db.session.commit()
        return ve


@video_embedding_ns.route("/<int:embedding_id>")
@video_embedding_ns.response(404, "VideoEmbedding not found")
class VideoEmbeddingAPI(Resource):

    @video_embedding_ns.marshal_with(video_embedding_model)
    def get(self, embedding_id):
        """Get a video embedding by ID"""
        ve = VideoEmbedding.query.get(embedding_id)
        if not ve:
            video_embedding_ns.abort(404, "VideoEmbedding not found")
        return ve

    def delete(self, embedding_id):
        """Delete a video embedding by ID"""
        ve = VideoEmbedding.query.get(embedding_id)
        if not ve:
            video_embedding_ns.abort(404, "VideoEmbedding not found")
        db.session.delete(ve)
        db.session.commit()
        return {"message": "VideoEmbedding deleted successfully"}, 200
