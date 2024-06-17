from sqlalchemy.orm import validates
from init import db, ma
from sqlalchemy import UniqueConstraint
from marshmallow import fields


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    agent = db.relationship('Agent', back_populates='appointments')
    user = db.relationship('User', back_populates='appointments')

    __table_args__ = (
        UniqueConstraint('date', 'time', 'agent_id', name='appointment_agent_uc'),
        UniqueConstraint('date', 'time', 'user_id', name='appointment_user_uc')
        )

    @validates('time')
    def validate_time(self, key, value):
        if value[-2:] not in ['00', '15', '30', '45']:
            raise ValueError('Invalid time. Minutes must be 00, 15, 30 or 45.')
        return value

class AppointmentSchema(ma.Schema):
    user = fields.Nested('UserSchema', only=['id', 'name', 'email', 'contact_number'])
    veterinarian = fields.Nested('VeterinarianSchema', only=['first_name', 'last_name', 'email'])

    class Meta:
        fields = ['id', 'date', 'time', 'veterinarian_id', 'veterinarian', 'patient', 'patient_id', 'patient.name']