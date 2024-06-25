from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from models.testimonial import Testimonial, TestimonialSchema  # Importing Testimonial model and schema
from init import db  # Importing the SQLAlchemy database instance
from blueprints.auth_bp import admin_or_owner_required  # Importing authorization function

testimonials_bp = Blueprint("testimonials", __name__, url_prefix="/testimonials")  # Creating a Blueprint for testimonials


# Get all testimonials
@testimonials_bp.route("/", methods=["GET"])
@jwt_required()  # Requires JWT token for access
def get_all_testimonials():
    stmt = db.select(Testimonial).order_by(Testimonial.id)  # SQLAlchemy select statement to fetch all testimonials
    testimonials = db.session.scalars(stmt).all()  # Executing the query to fetch all testimonials

    return TestimonialSchema(many=True, exclude=["agent_id", "user_id"]).dump(  # Serializing testimonials to JSON
        testimonials  # List of testimonials fetched from the database
    )


# Retrieve one testimonial
@testimonials_bp.route("/<int:testimonial_id>", methods=["GET"])
@jwt_required()  # Requires JWT token for access
def get_one_testimonial(testimonial_id):
    stmt = db.select(Testimonial).filter_by(id=testimonial_id)  # SQLAlchemy select statement for a specific testimonial
    testimonial = db.session.scalar(stmt)  # Fetching the testimonial from the database

    if testimonial:
        return TestimonialSchema(exclude=["agent_id", "user_id"]).dump(testimonial)  # Serializing the testimonial to JSON
    else:
        return {"error": "Testimonial not found"}, 404  # Returning error if testimonial not found


# Create testimonial
@testimonials_bp.route("/", methods=["POST"])
@jwt_required()  # Requires JWT token for access
def create_testimonial():
    try:
        testimonial = TestimonialSchema().load(request.json)  # Loading JSON data into Testimonial schema
        testimonial = Testimonial(
            property_address=testimonial["property_address"],  # Extracting property address from JSON
            comment=testimonial["comment"],  # Extracting comment from JSON
            rating=testimonial["rating"],  # Extracting rating from JSON
            date_created=date.today(),  # Setting current date as date created
            user_id=testimonial["user_id"],  # Extracting user ID from JSON
            agent_id=testimonial["agent_id"],  # Extracting agent ID from JSON
        )

        db.session.add(testimonial)  # Adding new testimonial to the database
        db.session.commit()  # Committing the transaction

        return TestimonialSchema(exclude=["agent_id", "user_id"]).dump(testimonial), 201  # Returning created testimonial
    except IntegrityError:
        return {"error": "User or Agent is not found"}, 409  # Handling IntegrityError if user or agent is not found


# Update testimonial
@testimonials_bp.route("/<int:testimonial_id>", methods=["PUT", "PATCH"])
@jwt_required()  # Requires JWT token for access
def update_testimonial(testimonial_id):
    testimonial = Testimonial.query.get(testimonial_id)  # Retrieving testimonial by ID from the database
    if testimonial:
        admin_or_owner_required(testimonial.user_id)  # Checking if user is admin or owner of testimonial

        testimonial_info = TestimonialSchema().load(request.json, partial=True)  # Loading JSON data into Testimonial schema
        testimonial.property_address = testimonial_info.get(
            "property_address", testimonial.property_address
        )  # Updating property address if present in JSON
        testimonial.comment = testimonial_info.get("comment", testimonial.comment)  # Updating comment if present in JSON
        testimonial.rating = testimonial_info.get("rating", testimonial.rating)  # Updating rating if present in JSON
        testimonial.user_id = testimonial_info.get("user_id", testimonial.user.id)  # Updating user ID if present in JSON
        testimonial.agent_id = testimonial_info.get("agent_id", testimonial.agent.id)  # Updating agent ID if present in JSON

        db.session.commit()  # Committing the transaction

        return TestimonialSchema(exclude=["agent_id", "user_id"]).dump(testimonial)  # Returning updated testimonial
    else:
        return {"error": "Testimonial not found"}, 404  # Returning error if testimonial not found


# Delete testimonial
@testimonials_bp.route("/<int:testimonial_id>", methods=["DELETE"])
@jwt_required()  # Requires JWT token for access
def delete_testimonial(testimonial_id):
    testimonial = Testimonial.query.get(testimonial_id)  # Retrieving testimonial by ID from the database
    if testimonial:
        admin_or_owner_required(testimonial.user_id)  # Checking if user is admin or owner of testimonial

        db.session.delete(testimonial)  # Deleting testimonial from the database
        db.session.commit()  # Committing the transaction

        return {"message": f"Testimonial ID - {testimonial.id} deleted successfully"}, 200  # Returning success message
    else:
        return {"error": "Testimonial not found"}, 404  # Returning error if testimonial not found
