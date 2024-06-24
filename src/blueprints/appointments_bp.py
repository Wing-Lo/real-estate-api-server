from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from models.appointment import Appointment, AppointmentSchema
from init import db
from blueprints.auth_bp import admin_required
from marshmallow.exceptions import ValidationError


appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


# Get all appointments
@appointments_bp.route("/", methods=["GET"])
@jwt_required()  # Get the JSON web token from the request
def get_all_appointments():
    stmt = db.select(Appointment).order_by(Appointment.id)
    appointments = db.session.scalars(stmt).all()

    if not appointments:
        return jsonify(message="No appointments found"), 404

    return AppointmentSchema(many=True, exclude=["agent_id","user_id"]).dump(appointments)


# Retrieve one testimonial
@appointments_bp.route("/<int:appointment_id>", methods=["GET"])
@jwt_required()  # Get the JSON web token from the request
def get_one_appointment(appointment_id):
    stmt = db.select(Appointment).filter_by(id=appointment_id)
    appointment = db.session.scalar(stmt)
    if appointment:
        return AppointmentSchema(exclude=["agent_id","user_id"]).dump(appointment)
    else:
        return {"error": "Appointment not found"}, 404

# create appointment
@appointments_bp.route("/", methods=["POST"])
@jwt_required()  # Get the JSON web token from the user as users must be logged in to add a review
def create_appointment():
    try:
        new_appointment = AppointmentSchema().load(request.json)
        
        # Validate date format (handled by Marshmallow schema)
        # Ensure appointment time meets custom validation rules
        appointment = Appointment(
            date=new_appointment["date"],
            time=new_appointment["time"],
            user_id=new_appointment["user_id"],
            agent_id=new_appointment["agent_id"],
        )

    except ValidationError as err:
        return {"message": str(err)}, 400
    except ValueError as err:
        return {"message": str(err)}, 400

    try:
        db.session.add(appointment)
        db.session.commit()
        return AppointmentSchema(exclude=["agent_id", "user_id"]).dump(appointment), 201
    except IntegrityError as e:
        db.session.rollback()
        if 'appointment_agent_uc' in str(e):
            return {"error": "Appointment with this date, time, and agent already exists."}, 409
        elif 'appointment_user_uc' in str(e):
            return {"error": "Appointment with this date, time, and user already exists."}, 409
        else:
            return {"error": "Database Integrity Error."}, 409
    except KeyError:
        db.session.rollback()
        return {"error": "Please provide all details of the appointment"}, 400
    
# # Update a testimonial
# @appointments_bp.route("/<int:testimonial_id>", methods=["PUT", "PATCH"])
# @jwt_required()
# def update_testimonial(testimonial_id):
#     testimonial = Testimonial.query.get(testimonial_id)
#     if testimonial:
#         admin_required()
#         testimonial_info = TestimonialSchema().load(request.json, partial=True)
#         testimonial.property_address = testimonial_info.get("property_address", testimonial.property_address)
#         testimonial.comment = testimonial_info.get("comment", testimonial.comment)
#         testimonial.rating = testimonial_info.get("rating", testimonial.rating)
#         testimonial.user_id = testimonial_info.get("user_id", testimonial.user.id)
#         testimonial.agent_id = testimonial_info.get("agent_id", testimonial.agent.id)

#         db.session.commit()
#         return TestimonialSchema(exclude=["agent_id","user_id"]).dump(testimonial)
#     else:
#         return {"error": "Testimonial not found"}, 404


# # Delete a testimonial - only admins can do this
# @appointments_bp.route("/<int:testimonial_id>", methods=["DELETE"])
# @jwt_required()
# def delete_testimonial(testimonial_id):
#     testimonial = Testimonial.query.get(testimonial_id)
#     if testimonial:
#         admin_required()
#         db.session.delete(testimonial)
#         db.session.commit()
#         return {"message": f"Testimonial ID - {testimonial.id} deleted successfully"}, 200
#     else:
#         return {"error": "Testimonial not found"}, 404
