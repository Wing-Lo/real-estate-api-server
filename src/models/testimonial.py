from marshmallow import fields, validate
from marshmallow.validate import Range
from init import db, ma 


class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    property_address = db.Column(db.String(250), nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.Date())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate="cascade", ondelete='cascade'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id', onupdate="cascade", ondelete='cascade'), nullable=False)

    user = db.relationship('User', back_populates='testimonials')
    agent = db.relationship('Agent', back_populates='testimonials')

class TestimonialSchema(ma.Schema):
    property_address = fields.String(required=True, validate=validate.Length(min=1, max=200))  # Property address is required and must be between 1 and 200 characters
    comment = fields.String(required=True, validate=validate.Length(min=10, max=1000))  # Comment is required and must be between 10 and 1000 characters
    rating = fields.Integer(required=True, validate=Range(min=0, max=5))  # Rating must be between 0 and 5
    date_created = fields.Date()
    user_id = fields.Integer(required=True, validate=validate.Range(min=1, error="User ID must be a positive integer"))  # User ID must be a positive integer (required)
    agent_id = fields.Integer(required=True, validate=validate.Range(min=1, error="Agent ID must be a positive integer"))  # Agent ID must be a positive integer (required)

    user = fields.Nested('UserSchema', only=['id', 'name', 'email', 'contact_number'])
    agent = fields.Nested('AgentSchema', only=['id', 'name', 'email', 'contact_number'])

    class Meta:
        fields = ('id', 'property_address', 'comment', 'rating', 'date_created', 'user', 'agent', 'user_id', 'agent_id')