from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.user import User, UserSchema
from init import db, bcrypt
from blueprints.auth_bp import admin_required, admin_or_owner_required


users_bp = Blueprint("users", __name__, url_prefix="/users")


# Get all users
@users_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_users():
    admin_required()

    stmt = db.select(User).order_by(User.id)
    users = db.session.scalars(stmt).all()

    return UserSchema(many=True, exclude=["password"]).dump(users)


# Get a one user
@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_one_user(user_id):
    admin_or_owner_required(user_id)

    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)

    if user:
        return UserSchema(exclude=["password"]).dump(user)
    else:
        return {"error": "User not found"}, 404


# Update a user - change name, email, or password
@users_bp.route("/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_user(user_id):
    user = User.query.get(user_id)

    if user:
        admin_or_owner_required(user_id)

        user_info = UserSchema().load(request.json, partial=True)
        user.name = user_info.get("name", user.name)
        user.email = user_info.get("email", user.email)
        user.password = bcrypt.generate_password_hash(
            user_info.get("password", user.password)
        ).decode("utf-8")
        user.contact_number = user_info.get("contact_number", user.contact_number)

        db.session.commit()

        return UserSchema(exclude=["password"]).dump(user)
    else:
        return {"error": "User not found"}, 404


# Update a user - make admin - only admins can do this
@users_bp.route("/make_admin/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
def make_admin(user_id):
    user = User.query.get(user_id)

    if user:
        admin_required()
        user.is_admin = True
        db.session.commit()

        return {"message": f"user {user.name} with ID {user.id} is now an admin"}, 200
    else:
        return {"error": "User not found"}, 404


# Delete a user - only admins can do this
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        admin_or_owner_required(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message": f"User {user.name} deleted successfully"}, 200
    else:
        return {"error": "User not found"}, 404
