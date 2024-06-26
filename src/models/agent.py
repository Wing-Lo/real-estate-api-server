from marshmallow import fields, validate
import enum
from marshmallow_enum import EnumField
from init import db, ma

# Enum for supported languages
class LanguagesEnum(enum.Enum):
    Mandarin = 1
    Cantonese = 2
    Korean = 3
    Japanese = 4
    Spanish = 5
    French = 6

# Agent model for SQLAlchemy
class Agent(db.Model):
    __tablename__ = 'agents'  # Define the table name

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(50), nullable=False)  # Agent's name
    email = db.Column(db.String(50), nullable=False, unique=True)  # Agent's email (must be unique)
    contact_number = db.Column(db.String(10), nullable=False)  # Agent's contact number
    overview = db.Column(db.Text)  # Agent's overview or bio
    languages = db.Column(db.ARRAY(db.Enum(LanguagesEnum)))  # Languages spoken by the agent

    # Relationship to appointments and testimonials
    appointments = db.relationship('Appointment', back_populates='agent', cascade='all, delete')
    testimonials = db.relationship('Testimonial', back_populates='agent', cascade='all, delete')

# Marshmallow schema for serializing/deserializing Agent model
class AgentSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))  # Name is required and must be between 1 and 100 characters
    email = fields.Email(required=True)  # Email is required
    contact_number = fields.String(required=True, validate=validate.Regexp(
        r'^\+?1?\d{9,15}$', error="Contact number must be a valid phone number"))  # Contact number must be valid phone number format
    overview = fields.String(required=True, validate=validate.Length(min=10, max=2000))  # Overview is required and must be between 10 and 2000 characters
    languages = fields.List(EnumField(LanguagesEnum), required=True, validate=validate.Length(min=1))  # List of languages, at least one language is required

    # Nested relationship field for appointments, only including specific fields
    appointments = fields.List(fields.Nested('AppointmentSchema', only=['date', 'time', 'user_id']))

    class Meta:
        fields = ('id', 'name', 'email', 'contact_number', 'overview', 'languages')  # Fields to include in the serialization