from marshmallow import fields
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
    property_address = fields.String(required=True)
    comment = fields.String(required=True)
    rating = fields.Integer(required=True, validate=Range(min=0, max=5))
    date_created = fields.Date()

    user = fields.Nested('UserSchema', only=['name'])
    agent = fields.Nested('CommentSchema', only=['id', 'name', 'email', 'contact_number'], many=True) 

    class Meta:
        fields = ('id', 'property_address', 'comment', 'rating', 'date_created', 'user', 'agent')