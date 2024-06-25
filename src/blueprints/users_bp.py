from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.user import User, UserSchema  # Importing User model and UserSchema
from init import db, bcrypt  # Importing SQLAlchemy database instance and bcrypt for password hashing
from blueprints.auth_bp import admin_required, admin_or_owner_required  # Importing authorization functions

users_bp = Blueprint("users", __name__, url_prefix="/users")  # Creating a Blueprint for users


# Get all users
@users_bp.route("/", methods=["GET"])
@jwt_required()  # Requires JWT token for access
def get_all_users():
    admin_required()  # Only admin can access all users

    stmt = db.select(User).order_by(User.id)  # SQLAlchemy select statement to fetch all users
    users = db.session.scalars(stmt).all()  # Executing the query to fetch all users

    return UserSchema(many=True, exclude=["password"]).dump(users)  # Serializing users to JSON, excluding password


# Get one user
@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()  # Requires JWT token for access
def get_one_user(user_id):
    admin_or_owner_required(user_id)  # Admin or owner can access the user

    stmt = db.select(User).filter_by(id=user_id)  # SQLAlchemy select statement for a specific user
    user = db.session.scalar(stmt)  # Fetching the user from the database

    if user:
        return UserSchema(exclude=["password"]).dump(user)  # Serializing the user to JSON, excluding password
    else:
        return {"error": "User not found"}, 404  # Returning error if user not found


# Update user - change name, email, password, or contact number
@users_bp.route("/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()  # Requires JWT token for access
def update_user(user_id):
    user = User.query.get(user_id)  # Retrieving user by ID from the database

    if user:
        admin_or_owner_required(user_id)  # Admin or owner can update the user

        user_info = UserSchema().load(request.json, partial=True)  # Loading JSON data into UserSchema
        user.name = user_info.get("name", user.name)  # Updating name if present in JSON
        user.email = user_info.get("email", user.email)  # Updating email if present in JSON
        user.password = bcrypt.generate_password_hash(  # Hashing and updating password if present in JSON
            user_info.get("password", user.password)
        ).decode("utf-8")
        user.contact_number = user_info.get("contact_number", user.contact_number)  # Updating contact number if present

        db.session.commit()  # Committing the transaction

        return UserSchema(exclude=["password"]).dump(user)  # Returning updated user, excluding password
    else:
        return {"error": "User not found"}, 404  # Returning error if user not found


# Make user admin - only admins can do this
@users_bp.route("/make_admin/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()  # Requires JWT token for access
def make_admin(user_id):
    user = User.query.get(user_id)  # Retrieving user by ID from the database

    if user:
        admin_required()  # Only admin can make a user an admin
        user.is_admin = True  # Setting user as admin
        db.session.commit()  # Committing the transaction

        return {"message": f"user {user.name} with ID {user.id} is now an admin"}, 200  # Returning success message
    else:
        return {"error": "User not found"}, 404  # Returning error if user not found


# Delete user - only admins can do this
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()  # Requires JWT token for access
def delete_user(user_id):
    user = User.query.get(user_id)  # Retrieving user by ID from the database

    if user:
        admin_or_owner_required(user_id)  # Admin or owner can delete the user
        db.session.delete(user)  # Deleting user from the database
        db.session.commit()  # Committing the transaction

        return {"message": f"User {user.name} deleted successfully"}, 200  # Returning success message
    else:
        return {"error": "User not found"}, 404  # Returning error if user not found
