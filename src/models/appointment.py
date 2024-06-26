from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint
from datetime import datetime, date
from marshmallow import fields, validate
from init import db, ma

# Appointment model for SQLAlchemy
class Appointment(db.Model):
    __tablename__ = 'appointments'  # Define the table name

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    date = db.Column(db.Date, nullable=False)  # Date of the appointment (required)
    time = db.Column(db.Time, nullable=False)  # Time of the appointment (required)

    # Foreign key to link appointment with user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', onupdate='cascade', ondelete='cascade'),
        nullable=False,
    )
    # Foreign key to link appointment with agent
    agent_id = db.Column(
        db.Integer,
        db.ForeignKey('agents.id', onupdate='cascade', ondelete='cascade'),
        nullable=False,
    )

    # Define relationships to User and Agent models
    agent = db.relationship('Agent', back_populates='appointments')  # Relationship with Agent model
    user = db.relationship('User', back_populates='appointments')  # Relationship with User model

    # Ensure unique combination of date, time, and agent_id
    __table_args__ = (
        UniqueConstraint('date', 'time', 'agent_id', name='appointment_agent_uc'),
        UniqueConstraint('date', 'time', 'user_id', name='appointment_user_uc'),
    )

    # Validator for date field
    @validates('date')
    def validate_date(self, key, value):
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(
                    'Invalid date format. Date must be in YYYY-MM-DD format.'
                )

        if not isinstance(value, date):
            raise ValueError('Invalid date type. Date must be a datetime.date object.')

        # Ensure date is in the future
        if value <= date.today():
            raise ValueError('Appointment date must be in the future.')

        return value

    # Validator for time field
    @validates('time')
    def validate_time(self, key, value):
        if isinstance(value, str):
            # Ensure time format HH:MM:SS
            try:
                datetime.strptime(value, '%H:%M:%S')
            except ValueError:
                raise ValueError('Invalid time format. Time must be in HH:MM:SS format.')

        # Ensure seconds are '00'
        if value[-2:] != '00':
            raise ValueError('Invalid time format. Seconds must be 00.')

        # Ensure valid minutes (00, 15, 30, 45)
        minutes = value[-5:-3]  # Adjust index for HH:MM:SS format
        if minutes not in ['00', '15', '30', '45']:
            raise ValueError('Invalid time. Minutes must be 00, 15, 30, or 45.')

        # Ensure hour is between 8 AM and 5 PM (08:00 to 17:00)
        hour = int(value[:2])
        if not (8 <= hour <= 17):
            raise ValueError('Invalid time. Hour must be between 08:00 and 17:00.')

        return value

# Marshmallow schema for serializing/deserializing Appointment model
class AppointmentSchema(ma.Schema):
    id = fields.Integer(dump_only=True)  # ID (output only)
    date = fields.String(required=True)  # Date of the appointment (required)
    time = fields.String(required=True)  # Time of the appointment (required)
    user_id = fields.Integer(required=True, validate=validate.Range(min=1, error="User ID must be a positive integer"))  # User ID must be a positive integer (required)
    agent_id = fields.Integer(required=True, validate=validate.Range(min=1, error="Agent ID must be a positive integer"))  # Agent ID must be a positive integer (required)

    # Nested field for user details (output only)
    user = fields.Nested(
        'UserSchema', only=['id', 'name', 'email', 'contact_number'], dump_only=True
    )
    # Nested field for agent details (output only)
    agent = fields.Nested(
        'AgentSchema', only=['id', 'name', 'email', 'contact_number'], dump_only=True
    )

    class Meta:
        fields = ['id', 'date', 'time', 'user_id', 'agent_id', 'user', 'agent']  # Fields to include in serialization
