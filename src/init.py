from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Initialize SQLAlchemy for database interactions
db = SQLAlchemy()
# Initialize Marshmallow for serialization/deserialization
ma = Marshmallow()
# Initialize Bcrypt for hashing passwords
bcrypt = Bcrypt()
# Initialize JWTManager for handling JSON Web Tokens
jwt = JWTManager()
