from datetime import timedelta
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity
from models.user import User, UserSchema
from init import bcrypt, db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Create a new user
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        user_info = UserSchema().load(request.json)  # Deserialize request JSON to UserSchema
        user = User(
            name=user_info["name"],
            email=user_info["email"],
            contact_number=user_info["contact_number"],
            password=bcrypt.generate_password_hash(user_info["password"]).decode("utf-8"),  # Hash password
        )
        db.session.add(user)  # Add user to session
        db.session.commit()  # Commit changes to database
        return UserSchema(exclude=["password"]).dump(user), 201  # Serialize user (exclude password field)
    except IntegrityError:
        return {"error": "Email address already in use"}, 409  # Return error if email is already in use


# Log in as a user
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        stmt = db.select(User).filter_by(email=request.json["email"])  # Query user by email
        user = db.session.scalar(stmt)  # Retrieve user

        if user and bcrypt.check_password_hash(user.password, request.json["password"]):
            # Check if user exists and password is correct
            token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))  # Create JWT token
            return {"token": token, "user": UserSchema(exclude=["password"]).dump(user)}  # Serialize token and user
        else:
            return {"error": "Invalid email address or password"}, 401  # Return error for invalid credentials
    except KeyError:
        return {"error": "Email and password are required"}, 400  # Return error if email or password not provided


# Authorization decorator - check if user is admin
def admin_required():
    user_id = get_jwt_identity()  # Get user ID from JWT token
    stmt = db.select(User).filter_by(id=user_id)  # Query user by ID
    user = db.session.scalar(stmt)  # Retrieve user

    if not (user and user.is_admin):  # Check if user exists and is admin
        raise PermissionError("You do not have authorization to access this resource.")


# Authorization decorator - check if user is admin or owner of a resource
def admin_or_owner_required(owner_id):
    user_id = get_jwt_identity()  # Get user ID from JWT token

    stmt = db.select(User).filter_by(id=user_id)  # Query user by ID
    user = db.session.scalar(stmt)  # Retrieve user

    # Check if user exists and is either an admin or the owner of the resource
    if not (user and (user.is_admin or user_id == owner_id)):
        raise PermissionError("You do not have authorization to access this resource.")
