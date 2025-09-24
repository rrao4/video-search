from flask import jsonify
from flask_restx import Resource, Namespace 
from api.api_models import user_model, user_input_model, login_model, login_input_model
from extensions import db
from db.models import User
from flask_login import current_user, login_user, logout_user, login_required

auth = Namespace("auth", description="Authentication related operations")

@auth.route("/signup")
class SignUpAPI(Resource):
    @auth.marshal_list_with(user_model)
    def get(self):
        return User.query.all()

    @auth.expect(user_input_model)
    @auth.marshal_with(user_model)
    def post(self):

        existing_user = User.query.filter_by(username=auth.payload["username"]).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400
    
        user = User(username=auth.payload["username"], 
                  email=auth.payload["email"],
                  password=auth.payload["password"],
                  )
        db.session.add(user)
        db.session.commit()
        #login_user(user)
        return user.to_dict(), 201

@auth.route("/login")
class LoginAPI(Resource):

    @auth.expect(login_input_model)
    @auth.marshal_with(login_model)
    def post(self):
        user = User.query.filter(User.username == auth.payload["username"] and User.check_password(auth.payload["password"])).first()
        if not user:
            return jsonify({"error": "User not found"}), 401
        return user.to_dict(), 201
        

    



