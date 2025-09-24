from flask import request
from flask_restx import Resource, Namespace, fields
from extensions import db
from db.models import Collection
from flask_login import current_user, login_required
from api.api_models import collection_model, collection_input_model

collection_ns = Namespace("collections", description="Collection related operations")

@collection_ns.route("")
class CollectionListAPI(Resource):
   
    @collection_ns.marshal_list_with(collection_model)
    # @login_required
    def get(self):
        """List all collections for the current user"""
        collections = Collection.query.all()
        return [collection.to_dict() for collection in collections], 200

    @collection_ns.expect(collection_input_model)
    @collection_ns.marshal_with(collection_model, code=201)
    # @login_required
    def post(self):
        """Create a new collection"""
        #data = request.json
        data = collection_ns.payload
        new_collection = Collection(
            collection_name=data["collection_name"],
            owner_id=data["owner_id"]   # <-- now coming from request
        )
        db.session.add(new_collection)
        db.session.commit()
        return new_collection, 201


    @collection_ns.marshal_with(collection_model)
    # @login_required
    def get(self, collection_id):
        """Get a collection by ID (must belong to current user)"""
        collection = Collection.query.filter_by(id=collection_id).first()
        # If user-specific:
        # collection = Collection.query.filter_by(id=collection_id, owner_id=current_user.id).first()
        if not collection:
            collection_ns.abort(404, "Collection not found")
        return collection

    # @login_required
    def delete(self, collection_id):
        """Delete a collection by ID (must belong to current user)"""
        collection = Collection.query.filter_by(
            id=collection_id, owner_id=current_user.id
        ).first()
        if not collection:
            collection_ns.abort(404, "Collection not found")

        db.session.delete(collection)
        db.session.commit()
        return {"message": "Collection deleted successfully"}, 200