from datetime import timedelta
from flask import Blueprint, request, abort, jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity
from models.user import User, UserSchema
from init import bcrypt, db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# Create a new user
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        user_info = UserSchema().load(request.json)
        user = User(
            name=user_info["name"],
            email=user_info["email"],
            contact_number=user_info["contact_number"],
            password=bcrypt.generate_password_hash(user_info["password"]).decode(
                "utf-8"
            ),
        )
        db.session.add(user)
        db.session.commit()
        return UserSchema(exclude=["password"]).dump(user), 201
    except IntegrityError:
        return {"error": "Email address already in use"}, 409


# Log in as a user
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        stmt = db.select(User).filter_by(email=request.json["email"])
        user = db.session.scalar(stmt)
        if user and bcrypt.check_password_hash(user.password, request.json["password"]):
            print("work")
            token = create_access_token(
                identity=user.id, expires_delta=timedelta(days=1)
            )
            return {"token": token, "user": UserSchema(exclude=["password"]).dump(user)}
        else:
            return {
                "error": "Invalid email address or password"
            }, 401  # If the email or password are not found in the database, return an error message
    except KeyError:
        return {
            "error": "Email and password are required"
        }, 400  # If either of the required keys are not provided, return an error message


def admin_required():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not (user and user.is_admin):
        raise PermissionError("You do not have authorization to access this resource.")

def admin_or_owner_required(owner_id):
    # Get the user id from the JSON web token
    user_id = get_jwt_identity()

    # Build and execute query to retrieve the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)

    # Check if the user exists and if the user is either an admin or the owner
    if not (user and (user.is_admin or user_id == owner_id)):
        raise PermissionError("You do not have authorization to access this resource.")
