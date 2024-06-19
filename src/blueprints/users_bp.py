from flask import Blueprint
from models.user import User, UserSchema
from init import db

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Get all users 
@users_bp.route('/', methods=['GET'])
def all_users():
    stmt = db.select(User).order_by(User.id) 
    users = db.session.scalars(stmt).all() 
    return UserSchema(many=True, exclude=['password']).dump(users) 

# Get a one user 
@users_bp.route('/<int:user_id>', methods=['GET'])
def one_user(user_id):
    stmt = db.select(User).filter_by(id=user_id) 
    user = db.session.scalar(stmt) 
    if user: 
        return UserSchema(exclude=['password']).dump(user)
    else:
        return {'error':'User not found'}, 404 