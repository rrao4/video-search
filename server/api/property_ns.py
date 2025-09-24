from flask import request
from flask_restx import Resource, Namespace, fields
from extensions import db
from db.models import Property, PropertyValue
from api.api_models import property_model, property_input_model, property_Filter_model
from sqlalchemy.orm import joinedload
property_ns = Namespace("properties", description="Property related operations")

# =====================================================
# Property Endpoints
# =====================================================
@property_ns.route("")
class PropertyListAPI(Resource):

    @property_ns.marshal_list_with(property_Filter_model)
    def get(self):
        """Get all properties"""
        from sqlalchemy.orm import joinedload

        properties = (
            Property.query.options(
                joinedload(Property.children).joinedload(Property.values),  # children + their values
                joinedload(Property.values)  # current property’s values
            )
            .filter(Property.parent_id.is_(None))
            .order_by(Property.display_order)
            .all()
        )
        return [prop.to_filter_dict() for prop in properties], 200

    @property_ns.expect(property_input_model)
    @property_ns.marshal_with(property_model, code=201)
    def post(self):
        """Create a new property"""
        data = property_ns.payload
        prop = Property(
            name=data["name"],
            parent_id=data.get("parent_id"),
            display_order=data.get("display_order"),
        )
        db.session.add(prop)
        db.session.commit()
        return prop


@property_ns.route("/<int:property_id>")
@property_ns.response(404, "Property not found")
class PropertyAPI(Resource):

    @property_ns.marshal_with(property_model)
    def get(self, property_id):
        """Get a property by ID"""
        prop = Property.query.get(property_id)
        if not prop:
            property_ns.abort(404, "Property not found")
        return prop
