from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from models.appointment import Appointment, AppointmentSchema  # Import Appointment model and schema
from init import db
from blueprints.auth_bp import admin_required, admin_or_owner_required  # Import authorization decorators

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")  # Blueprint definition

# Get all appointments (admin only)
@appointments_bp.route("/", methods=["GET"])
@jwt_required()  # JWT token required for authentication
def get_all_appointments():
    admin_required()  # Ensure user is admin

    appointments = Appointment.query.order_by(Appointment.id).all()  # Query all appointments

    if not appointments:
        return {"error": "Appointment not found"}, 404  # Return error if no appointments found

    return AppointmentSchema(many=True, exclude=["agent_id", "user_id"]).dump(appointments)  # Serialize appointments


# Retrieve one appointment by ID (admin or owner)
@appointments_bp.route("/<int:appointment_id>", methods=["GET"])
@jwt_required()  # JWT token required for authentication
def get_one_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)  # Query appointment by ID

    if not appointment:
        return {"error": "Appointment not found"}, 404  # Return error if appointment with given ID not found

    admin_or_owner_required(appointment.user_id)  # Ensure user is admin or owner of the appointment

    return AppointmentSchema(exclude=["agent_id", "user_id"]).dump(appointment)  # Serialize appointment


# Create a new appointment (admin only)
@appointments_bp.route("/", methods=["POST"])
@jwt_required()  # JWT token required for authentication
def create_appointment():
    try:
        new_appointment = AppointmentSchema().load(request.json)  # Deserialize request JSON to AppointmentSchema

        appointment = Appointment(  # Create new Appointment object
            date=new_appointment["date"],
            time=new_appointment["time"],
            user_id=new_appointment["user_id"],
            agent_id=new_appointment["agent_id"],
        )

        db.session.add(appointment)  # Add appointment to session
        db.session.commit()  # Commit changes to database

        return AppointmentSchema(exclude=["agent_id", "user_id"]).dump(appointment), 201  # Serialize appointment

    except IntegrityError as e:
        db.session.rollback()  # Rollback in case of IntegrityError

        if "appointment_agent_uc" in str(e):
            return {"error": "Appointment with this date, time, and agent already exists."}, 409  # Conflict error

        elif "appointment_user_uc" in str(e):
            return {"error": "Appointment with this date, time, and user already exists."}, 409  # Conflict error

        else:
            return {"error": "User or Agent is not found"}, 409  # Other IntegrityError


# Update an appointment by ID (admin or owner)
@appointments_bp.route("/<int:appointment_id>", methods=["PUT", "PATCH"])
@jwt_required()  # JWT token required for authentication
def update_appointment(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)  # Retrieve appointment by ID

        if not appointment:
            return {"error": "Appointment not found"}, 404  # Return error if appointment with given ID not found

        admin_or_owner_required(appointment.user_id)  # Ensure user is admin or owner of the appointment

        appointment_info = AppointmentSchema().load(request.json, partial=True)  # Deserialize request JSON (partial update)
        appointment.date = appointment_info.get("date", appointment.date)  # Update appointment attributes
        appointment.time = appointment_info.get("time", appointment.time)
        appointment.user_id = appointment_info.get("user_id", appointment.user_id)
        appointment.agent_id = appointment_info.get("agent_id", appointment.agent_id)

        db.session.commit()  # Commit changes to database

        return AppointmentSchema(exclude=["agent_id", "user_id"]).dump(appointment), 200  # Serialize updated appointment

    except IntegrityError as e:
        db.session.rollback()  # Rollback in case of IntegrityError

        if "appointment_agent_uc" in str(e):
            return {"error": "Appointment with this date, time, and agent already exists."}, 409  # Conflict error

        elif "appointment_user_uc" in str(e):
            return {"error": "Appointment with this date, time, and user already exists."}, 409  # Conflict error

        else:
            return {"error": "User or Agent is not found"}, 409  # Other IntegrityError


# Delete an appointment by ID (admin or owner)
@appointments_bp.route("/<int:appointment_id>", methods=["DELETE"])
@jwt_required()  # JWT token required for authentication
def delete_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)  # Retrieve appointment by ID

    if not appointment:
        return {"error": "Appointment not found"}, 404  # Return error if appointment with given ID not found

    admin_or_owner_required(appointment.user_id)  # Ensure user is admin or owner of the appointment

    db.session.delete(appointment)  # Delete appointment from database
    db.session.commit()  # Commit changes

    return {"message": f"Appointment ID - {appointment.id} deleted successfully"}, 200  # Return success message
