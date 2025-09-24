from flask import request
from flask_restx import Resource, Namespace, fields
from extensions import db
from db.models import VideoPropertyValue, Video, PropertyValue
from api.api_models import video_property_value_model, video_property_value_input_model

video_property_value_ns = Namespace("video-property-values", description="VideoPropertyValue operations")



# =====================================================
# VideoPropertyValue Endpoints
# =====================================================
@video_property_value_ns.route("")
class VideoPropertyValueListAPI(Resource):

    @video_property_value_ns.marshal_list_with(video_property_value_model)
    def get(self):
        """List all video-property assignments"""
        return VideoPropertyValue.query.all()

    @video_property_value_ns.expect(video_property_value_input_model)
    @video_property_value_ns.marshal_with(video_property_value_model, code=201)
    def post(self):
        """Assign a property value to a video"""
        data = video_property_value_ns.payload

        # Validate video exists
        video = Video.query.get(data["video_id"])
        if not video:
            video_property_value_ns.abort(400, "Video does not exist")

        # Validate property value exists
        pv = PropertyValue.query.get(data["property_value_id"])
        if not pv:
            video_property_value_ns.abort(400, "PropertyValue does not exist")

        # Optional: prevent duplicate assignment
        existing = VideoPropertyValue.query.filter_by(
            video_id=data["video_id"],
            property_value_id=data["property_value_id"]
        ).first()
        if existing:
            video_property_value_ns.abort(400, "This property value is already assigned to the video")

        vpv = VideoPropertyValue(
            video_id=data["video_id"],
            property_value_id=data["property_value_id"]
        )
        db.session.add(vpv)
        db.session.commit()
        return vpv

# @video_property_value_ns.route("/<int:id>")
# @video_property_value_ns.response(404, "VideoPropertyValue not found")
# class VideoPropertyValueAPI(Resource):

#     @video_property_value_ns.marshal_with(video_property_value_model)
#     def get(self, id):
#         """Get a video-property assignment by ID"""
#         vpv = VideoPropertyValue.query.get(id)
#         if not vpv:
#             video_property_value_ns.abort(404, "VideoPropertyValue not found")
#         return vpv

#     @video_property_value_ns.expect(video_property_value_input_model)
#     @video_property_value_ns.marshal_with(video_property_value_model)
#     def put(self, id):
#         """Update a video-property assignment"""
#         vpv = VideoPropertyValue.query.get(id)
#         if not vpv:
#             video_property_value_ns.abort(404, "VideoPropertyValue not found")

#         data = request.json

#         # Validate video and property_value exist
#         if not Video.query.get(data["video_id"]):
#             video_property_value_ns.abort(400, "Video does not exist")
#         if not PropertyValue.query.get(data["property_value_id"]):
#             video_property_value_ns.abort(400, "PropertyValue does not exist")

#         vpv.video_id = data["video_id"]
#         vpv.property_value_id = data["property_value_id"]
#         db.session.commit()
#         return vpv

#     def delete(self, id):
#         """Delete a video-property assignment"""
#         vpv = VideoPropertyValue.query.get(id)
#         if not vpv:
#             video_property_value_ns.abort(404, "VideoPropertyValue not found")

#         db.session.delete(vpv)
#         db.session.commit()
#         return {"message": "VideoPropertyValue deleted successfully"}, 200
