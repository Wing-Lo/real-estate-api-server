from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from models.testimonial import Testimonial, TestimonialSchema
from init import db
from blueprints.auth_bp import admin_or_owner_required

testimonials_bp = Blueprint("testimonials", __name__, url_prefix="/testimonials")


# Get all testimonials
@testimonials_bp.route("/", methods=["GET"])
@jwt_required()  # Get the JSON web token from the request
def get_all_testimonials():
    stmt = db.select(Testimonial).order_by(Testimonial.id)
    testimonials = db.session.scalars(stmt).all()

    return TestimonialSchema(many=True, exclude=["agent_id", "user_id"]).dump(
        testimonials
    )


# Retrieve one testimonial
@testimonials_bp.route("/<int:testimonial_id>", methods=["GET"])
@jwt_required()  # Get the JSON web token from the request
def get_one_testimonial(testimonial_id):
    stmt = db.select(Testimonial).filter_by(id=testimonial_id)
    testimonial = db.session.scalar(stmt)

    if testimonial:
        return TestimonialSchema(exclude=["agent_id", "user_id"]).dump(testimonial)
    else:
        return {"error": "Testimonial not found"}, 404


# create testimonial
@testimonials_bp.route("/", methods=["POST"])
@jwt_required()  # Get the JSON web token from the user as users must be logged in to add a review
def create_testimonial():
    try:
        testimonial = TestimonialSchema().load(request.json)
        testimonial = Testimonial(
            property_address=testimonial["property_address"],
            comment=testimonial["comment"],
            rating=testimonial["rating"],
            date_created=date.today(),
            user_id=testimonial["user_id"],
            agent_id=testimonial["agent_id"],
        )

        db.session.add(testimonial)
        db.session.commit()

        return TestimonialSchema(exclude=["agent_id", "user_id"]).dump(testimonial), 201
    except IntegrityError:
        return {"error": "User or Agent is not found"}, 409


# Update a testimonial
@testimonials_bp.route("/<int:testimonial_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_testimonial(testimonial_id):
    testimonial = Testimonial.query.get(testimonial_id)
    if testimonial:
        admin_or_owner_required(testimonial.user_id)

        testimonial_info = TestimonialSchema().load(request.json, partial=True)
        testimonial.property_address = testimonial_info.get(
            "property_address", testimonial.property_address
        )
        testimonial.comment = testimonial_info.get("comment", testimonial.comment)
        testimonial.rating = testimonial_info.get("rating", testimonial.rating)
        testimonial.user_id = testimonial_info.get("user_id", testimonial.user.id)
        testimonial.agent_id = testimonial_info.get("agent_id", testimonial.agent.id)

        db.session.commit()

        return TestimonialSchema(exclude=["agent_id", "user_id"]).dump(testimonial)
    else:
        return {"error": "Testimonial not found"}, 404


# Delete a testimonial - only admins can do this
@testimonials_bp.route("/<int:testimonial_id>", methods=["DELETE"])
@jwt_required()
def delete_testimonial(testimonial_id):
    testimonial = Testimonial.query.get(testimonial_id)

    if testimonial:
        admin_or_owner_required(testimonial.user_id)

        db.session.delete(testimonial)
        db.session.commit()

        return {
            "message": f"Testimonial ID - {testimonial.id} deleted successfully"
        }, 200
    else:
        return {"error": "Testimonial not found"}, 404
