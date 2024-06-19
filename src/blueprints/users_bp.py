from flask import Blueprint
from models.user import User, UserSchema
from init import db, bcrypt

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Get all users 
@users_bp.route('/', methods=['GET'])
def all_users():
    stmt = db.select(User).order_by(User.id) # Prepares the query to retrieve all users 
    users = db.session.scalars(stmt).all() # Executes the query 
    return UserSchema(many=True, exclude=['password']).dump(users) # Returns all users excluding passwords, and their reviews for security and clarity

# Get a one user 
@users_bp.route('/<int:user_id>', methods=['GET'])
def one_user(user_id):
    stmt = db.select(User).filter_by(id=user_id) # Prepares the query to get a user with an id that matches the id that was passed in
    user = db.session.scalar(stmt) # Executes the query
    if user: # If the user is truthy (if the user exists) then return the user
        return UserSchema(exclude=['password']).dump(user)
    else:
        return {'error':'User not found'}, 404 # If the user does not exist return a corresponding error message
