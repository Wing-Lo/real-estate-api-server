from marshmallow import fields
from marshmallow.validate import Range
from init import db, ma

# Testimonial model for SQLAlchemy
class Testimonial(db.Model):
    __tablename__ = 'testimonials'  # Define the table name

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    property_address = db.Column(db.String(250), nullable=False)  # Property address (required)
    comment = db.Column(db.Text(), nullable=False)  # Comment (required)
    rating = db.Column(db.Integer, nullable=False)  # Rating (required)
    date_created = db.Column(db.Date())  # Date created (optional)

    # Foreign keys to link testimonial with user and agent
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', onupdate="cascade", ondelete='cascade'),
        nullable=False,
    )
    agent_id = db.Column(
        db.Integer,
        db.ForeignKey('agents.id', onupdate="cascade", ondelete='cascade'),
        nullable=False,
    )

    # Define relationships to User and Agent models
    user = db.relationship('User', back_populates='testimonials')  # Relationship with User model
    agent = db.relationship('Agent', back_populates='testimonials')  # Relationship with Agent model

# Marshmallow schema for serializing/deserializing Testimonial model
class TestimonialSchema(ma.Schema):
    property_address = fields.String(required=True)  # Property address is required
    comment = fields.String(required=True)  # Comment is required
    rating = fields.Integer(required=True, validate=Range(min=0, max=5))  # Rating is required and must be between 0 and 5
    date_created = fields.Date()  # Date created (optional)

    user_id = fields.Integer(required=True)  # User ID associated with the testimonial (required)
    agent_id = fields.Integer(required=True)  # Agent ID associated with the testimonial (required)

    # Nested field for user details
    user = fields.Nested('UserSchema', only=['id', 'name', 'email', 'contact_number'])

    # Nested field for agent details
    agent = fields.Nested('AgentSchema', only=['id', 'name', 'email', 'contact_number'])

    class Meta:
        fields = ('id', 'property_address', 'comment', 'rating', 'date_created', 'user', 'agent', 'user_id', 'agent_id')
        # Fields to include in serialization
