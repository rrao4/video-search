from flask_restx import fields

from extensions import api 

parent_property_model = api.model("ParentProperty", {
    "id": fields.Integer,
    "name": fields.String,
})

video_model = api.model("Video", {
    "id": fields.Integer(readonly=True),
    "path": fields.String(required=True),
    "aspect_ratio": fields.String,
    "genre": fields.String,
    "created_at": fields.DateTime,
    "descriptions": fields.List(fields.String),
    "properties": fields.List(fields.Nested(api.model("PropertyValue", {
        "property_id": fields.Integer,
        "property_name": fields.String,
        "parent_property": fields.Nested(parent_property_model, allow_null=True),
        "value_id": fields.Integer,
        "value": fields.String
    })))
})

video_input_model = api.model("VideoInput", {
    "path": fields.String,
    "aspect_ratio": fields.String,
    "genre": fields.String,
})

user_model = api.model("user", {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "password": fields.String,
    
})

user_input_model = api.model("UserInput", {
    "username": fields.String,
    "email": fields.String,
    "password": fields.String,
})

login_model = api.model("user", {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "password": fields.String,
    
})

login_input_model = api.model("LoginInput", {
    "username": fields.String,
    "password": fields.String,
})

collection_model = api.model("Collection", {
    "id": fields.Integer(readonly=True),
    "collection_name": fields.String(required=True, description="Name of the collection"),
    "owner_id": fields.Integer(readonly=True),
})

collection_input_model = api.model("CollectionInput", {
    "collection_name": fields.String(required=True, description="Name of the collection"),
    "owner_id": fields.Integer(required=True, description="ID of the collection owner"),
})

property_model = api.model("Property", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True, description="Property name"),
    "parent_id": fields.Integer(description="Parent property ID"),
    "display_order": fields.Integer(description="Display order"),
})

property_input_model = api.model("PropertyInput", {
    "name": fields.String(required=True, description="Property name"),
    "parent_id": fields.Integer(description="Parent property ID"),
    "display_order": fields.Integer(description="Display order"),
})

property_value_model = api.model("PropertyValue", {
    "id": fields.Integer(readonly=True),
    "property_id": fields.Integer(required=True, description="ID of the property"),
    "value": fields.String(required=True, description="Value string"),
    "display_order": fields.Integer(description="Display order"),
})

property_value_input_model = api.model("PropertyValueInput", {
    "property_id": fields.Integer(required=True, description="ID of the property"),
    "value": fields.String(required=True, description="Value string"),
    "display_order": fields.Integer(description="Display order"),
})



property_value_Filter_model = api.model("PropertyValue", {
    "id": fields.Integer(readonly=True),
    "value": fields.String(required=True, description="Property value"),
})

# Child property model (1 level deep)
property_child_model = api.model("PropertyChild", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True, description="Child property name"),
    "display_order": fields.Integer(description="Display order"),
    "values": fields.List(fields.Nested(property_value_model)),
})

# Main property model with children + values
property_Filter_model = api.model("Property", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True, description="Property name"),
    "parent_id": fields.Integer(description="Parent property ID"),
    "display_order": fields.Integer(description="Display order"),
    "values": fields.List(fields.Nested(property_value_Filter_model)),
    "children": fields.List(fields.Nested(property_child_model)),
})


video_embedding_model = api.model("VideoEmbedding", {
    "id": fields.Integer(readonly=True),
    "video_id": fields.Integer(required=True, description="ID of the video"),
    "embedding": fields.List(fields.Float, required=True, description="Vector embedding"),
})

video_embedding_input_model = api.model("VideoEmbeddingInput", {
    "video_id": fields.Integer(required=True, description="ID of the video"),
    "embedding": fields.List(fields.Float, required=True, description="Vector embedding"),
})

video_description_model = api.model("VideoDescription", {
    "id": fields.Integer(readonly=True),
    "video_id": fields.Integer(required=True, description="ID of the video"),
    "description": fields.String(required=True, description="Video description text"),
})

video_description_input_model = api.model("VideoDescriptionInput", {
    "video_id": fields.Integer(required=True, description="ID of the video"),
    "description": fields.String(required=True, description="Video description text"),
})

video_property_value_model = api.model("VideoPropertyValue", {
    "id": fields.Integer(readonly=True),
    "video_id": fields.Integer(required=True),
    "property_value_id": fields.Integer(required=True),
})

video_property_value_input_model = api.model("VideoPropertyValueInput", {
    "video_id": fields.Integer(required=True, description="ID of the video"),
    "property_value_id": fields.Integer(required=True, description="ID of the property value"),
})