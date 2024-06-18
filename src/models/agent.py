from marshmallow import fields
from sqlalchemy.orm import validates
import enum
from marshmallow_enum import EnumField
from init import db, ma


class LanguagesEnum(enum.Enum):
    Mandarin = 1
    Cantonese = 2
    Korean = 3
    Japanese = 4
    Spanish = 5
    French = 6


class Agent(db.Model):
    __tablename__ = 'agents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    contact_number = db.Column(db.String(10), nullable=False)
    overview = db.Column(db.Text)
    languages = db.Column(db.ARRAY(db.Enum(LanguagesEnum)))

    appointments = db.relationship('Appointment', back_populates='agent', cascade='all, delete')
    testimonials = db.relationship('Testimonial', back_populates='agent', cascade='all, delete')


class AgentSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    contact_number = fields.String(required=True)
    overview = fields.String(required=True)
    languages = fields.List(EnumField(LanguagesEnum))
    appointments = fields.List(fields.Nested('AppointmentSchema', only=['date', 'time', 'user_id']))

    class Meta:
        fields = ('id', 'name', 'email', 'contact_number', 'overview', 'languages', 'appointments')
