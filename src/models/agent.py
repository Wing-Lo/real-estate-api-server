from marshmallow import fields
from sqlalchemy.orm import validates
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
    name = fields.String(required=True)  # Name is required
    email = fields.Email(required=True)  # Email is required
    contact_number = fields.String(required=True)  # Contact number is required
    overview = fields.String(required=True)  # Overview is required
    languages = fields.List(EnumField(LanguagesEnum))  # List of languages

    # Nested relationship field for appointments, only including specific fields
    appointments = fields.List(fields.Nested('AppointmentSchema', only=['date', 'time', 'user_id']))

    class Meta:
        fields = ('id', 'name', 'email', 'contact_number', 'overview', 'languages')  # Fields to include in the serialization