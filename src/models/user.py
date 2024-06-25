from marshmallow import fields
from marshmallow.validate import Length
from init import db, ma

# User model for SQLAlchemy
class User(db.Model):
    __tablename__ = "users"  # Define the table name

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(50), nullable=False)  # User's name
    email = db.Column(db.String, nullable=False, unique=True)  # User's email (must be unique)
    contact_number = db.Column(db.String(10), nullable=False)  # User's contact number
    password = db.Column(db.String, nullable=False)  # User's password
    is_admin = db.Column(db.Boolean, default=False)  # Indicates if the user is an admin

    # Relationship to appointments and testimonials
    appointments = db.relationship('Appointment', back_populates='user', cascade='all, delete')
    testimonials = db.relationship('Testimonial', back_populates='user', cascade='all, delete')

# Marshmallow schema for serializing/deserializing User model
class UserSchema(ma.Schema):
    name = fields.String(required=True)  # Name is required
    email = fields.Email(required=True)  # Email is required
    contact_number = fields.String(required=True)  # Contact number is required
    password = fields.String(required=True, validate=Length(min=8))  # Password is required and must be at least 8 characters long

    # Nested relationship field for appointments, excluding the user field
    appointments = fields.List(fields.Nested('AppointmentSchema', exclude=['user']))

    class Meta:
        fields = ('id', 'name', 'email', 'contact_number', 'password', 'is_admin')  # Fields to include in the serialization