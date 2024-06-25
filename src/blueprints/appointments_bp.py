from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from marshmallow.exceptions import ValidationError
from models.appointment import Appointment, AppointmentSchema
from init import db
from blueprints.auth_bp import admin_required, admin_or_owner_required

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


# Get all appointments
@appointments_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_appointments():
    try:
        admin_required()

        appointments = Appointment.query.order_by(Appointment.id).all()

        if not appointments:
            return {"error": "Appointment not found"}, 404

        return AppointmentSchema(many=True, exclude=["agent_id", "user_id"]).dump(
            appointments
        )

    except PermissionError as e:
        return {"error": str(e)}, 403

    except Exception as e:
        return {"error": str(e)}, 500


# Retrieve one appointment
@appointments_bp.route("/<int:appointment_id>", methods=["GET"])
@jwt_required()
def get_one_appointment(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)

        if not appointment:
            return {"error": "Appointment not found"}, 404

        admin_or_owner_required(appointment.user_id)

        return AppointmentSchema(exclude=["agent_id", "user_id"]).dump(appointment)

    except PermissionError as e:
        return {"error": str(e)}, 403

    except Exception as e:
        return {"error": str(e)}, 500


# Create appointment
@appointments_bp.route("/", methods=["POST"])
@jwt_required()
def create_appointment():
    try:
        new_appointment = AppointmentSchema().load(request.json)

        appointment = Appointment(
            date=new_appointment["date"],
            time=new_appointment["time"],
            user_id=new_appointment["user_id"],
            agent_id=new_appointment["agent_id"],
        )

        db.session.add(appointment)
        db.session.commit()

        return AppointmentSchema(exclude=["agent_id", "user_id"]).dump(appointment), 201

    except ValidationError as err:
        db.session.rollback()
        return {"message": str(err)}, 400

    except IntegrityError as e:
        db.session.rollback()
        if "appointment_agent_uc" in str(e):
            return {
                "error": "Appointment with this date, time, and agent already exists."
            }, 409
        elif "appointment_user_uc" in str(e):
            return {
                "error": "Appointment with this date, time, and user already exists."
            }, 409
        else:
            return {"error": "Database Integrity Error."}, 409

    except KeyError:
        db.session.rollback()
        return {"error": "Please provide all details of the appointment"}, 400

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


# Update an appointment
@appointments_bp.route("/<int:appointment_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_appointment(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return {"error": "Appointment not found"}, 404

        admin_or_owner_required(appointment.user_id)

        appointment_info = AppointmentSchema().load(request.json)
        appointment.date = appointment_info.get("date", appointment.date)
        appointment.time = appointment_info.get("time", appointment.time)
        appointment.user_id = appointment_info.get("user_id", appointment.user_id)
        appointment.agent_id = appointment_info.get("agent_id", appointment.agent_id)

        db.session.commit()

        return AppointmentSchema(exclude=["agent_id", "user_id"]).dump(appointment), 200

    except KeyError:
        db.session.rollback()
        return {"error": "Please provide all details of the appointment"}, 400

    except ValidationError as err:
        db.session.rollback()
        return {"message": str(err)}, 400

    except IntegrityError as e:
        db.session.rollback()
        if "appointment_agent_uc" in str(e):
            return {
                "error": "Appointment with this date, time, and agent already exists."
            }, 409
        elif "appointment_user_uc" in str(e):
            return {
                "error": "Appointment with this date, time, and user already exists."
            }, 409
        else:
            return {"error": "User or Agent is not found"}, 409

    except PermissionError as e:
        return {"error": str(e)}, 403

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


# Delete an appointment - only admin and appointment owner can do this
@appointments_bp.route("/<int:appointment_id>", methods=["DELETE"])
@jwt_required()
def delete_appointment(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return {"error": "Appointment not found"}, 404

        admin_or_owner_required(appointment.user_id)

        db.session.delete(appointment)
        db.session.commit()

        return {
            "message": f"Appointment ID - {appointment.id} deleted successfully"
        }, 200

    except PermissionError as e:
        return {"error": str(e)}, 403

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
