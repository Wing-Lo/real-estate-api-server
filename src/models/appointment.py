from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint
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

    @validates('time')
    def validate_time(self, key, value):
        if value[-2:] not in ['00', '15', '30', '45']:
            raise ValueError('Invalid time. Minutes must be 00, 15, 30 or 45.')
        return value

class AppointmentSchema(ma.Schema):
    user = fields.Nested('UserSchema', only=['id', 'name', 'email', 'contact_number'])
    agent = fields.Nested('AgentSchema', only=['name', 'email', 'contact_number'])

    class Meta:
        fields = ['id', 'date', 'time', 'agent_id', 'agent', 'user', 'user_id']