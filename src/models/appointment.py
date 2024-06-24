from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint
from datetime import datetime, date
from marshmallow import fields
from init import db, ma

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate="cascade", ondelete='cascade'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id', onupdate="cascade", ondelete='cascade'), nullable=False)

    agent = db.relationship('Agent', back_populates='appointments')
    user = db.relationship('User', back_populates='appointments')

    __table_args__ = (
        UniqueConstraint('date', 'time', 'agent_id', name='appointment_agent_uc'),
        UniqueConstraint('date', 'time', 'user_id', name='appointment_user_uc')
        )

    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError('Invalid date type. Date must be a datetime.date object.')

        # Ensure date is in the future
        if value <= date.today():
            raise ValueError('Appointment date must be in the future.')

        return value

    @validates('time')
    def validate_time(self, key, value):
        # Ensure seconds are '00'
        if value[-2:] != '00':
            raise ValueError('Invalid time format. Seconds must be 00.')

        # Ensure valid minutes
        minutes = value[-5:-3]  # Adjust index for HH:MM:SS format
        if minutes not in ['00', '15', '30', '45']:
            raise ValueError('Invalid time. Minutes must be 00, 15, 30, or 45.')

        # Ensure hour is between 8 AM and 5 PM (08:00 to 17:00)
        hour = int(value[:2])
        if not (8 <= hour <= 17):
            raise ValueError('Invalid time. Hour must be between 08:00 and 17:00.')

        return value

class AppointmentSchema(ma.Schema):
    date = fields.Date()
    time = fields.String(required=True)
    user_id = fields.Integer(required=True)
    agent_id = fields.Integer(required=True)

    user = fields.Nested('UserSchema', only=['id', 'name', 'email', 'contact_number'])
    agent = fields.Nested('AgentSchema', only=['name', 'email', 'contact_number'])

    class Meta:
        fields = ['id', 'date', 'time', 'agent_id', 'agent', 'user', 'user_id']