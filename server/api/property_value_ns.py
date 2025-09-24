from flask import request
from flask_restx import Resource, Namespace, fields
from extensions import db
from db.models import PropertyValue, Property
from api.api_models import property_value_model, property_value_input_model

property_value_ns = Namespace("property-values", description="PropertyValue related operations")



# =====================================================
# PropertyValue Endpoints
# =====================================================
@property_value_ns.route("")
class PropertyValueListAPI(Resource):

    @property_value_ns.marshal_list_with(property_value_model)
    def get(self):
        """Get all property values"""
        return PropertyValue.query.all()

    @property_value_ns.expect(property_value_input_model)
    @property_value_ns.marshal_with(property_value_model, code=201)
    def post(self):
        """Create a new property value"""
        data = property_value_ns.payload
        # Optional: check if property exists
        if not Property.query.get(data["property_id"]):
            property_value_ns.abort(400, "Property ID does not exist")

        pv = PropertyValue(
            property_id=data["property_id"],
            value=data["value"],
            display_order=data.get("display_order"),
        )
        db.session.add(pv)
        db.session.commit()
        return pv


@property_value_ns.route("/<int:property_value_id>")
@property_value_ns.response(404, "PropertyValue not found")
class PropertyValueAPI(Resource):

    @property_value_ns.marshal_with(property_value_model)
    def get(self, property_value_id):
        """Get a property value by ID"""
        pv = PropertyValue.query.get(property_value_id)
        if not pv:
            property_value_ns.abort(404, "PropertyValue not found")
        return pv
