from marshmallow import fields
from marshmallow.validate import Length
from init import db, ma


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    contact_number = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    appointments = db.relationship('Appointments', back_populates='user', cascade='all, delete')

class UserSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    contact_number = fields.String(required=True)
    password = fields.String(required=True, validate=Length(min=8))

    appointments = fields.List(fields.Nested('AppointmentSchema', exclude=['user']))

    class Meta:
        fields = ('id', 'name', 'email', 'contact_number', 'password', 'is_admin')