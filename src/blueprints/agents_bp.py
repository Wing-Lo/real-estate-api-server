from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import date
from models.agent import Agent, AgentSchema
from init import db, bcrypt
from blueprints.auth_bp import admin_required

agents_bp = Blueprint("agents", __name__, url_prefix="/agents")


# Get all agents
@agents_bp.route("/", methods=["GET"])
@jwt_required()  # Get the JSON web token from the request
def get_all_agents():
    stmt = db.select(Agent).order_by(Agent.id)
    agents = db.session.scalars(stmt).all()

    if not agents:
        return {"error": "Agents not found"}, 404

    return AgentSchema(many=True).dump(agents)


# Retrieve one agent
@agents_bp.route("/<int:agent_id>", methods=["GET"])
@jwt_required()  # Get the JSON web token from the request
def get_one_agent(agent_id):
    stmt = db.select(Agent).filter_by(id=agent_id)
    agent = db.session.scalar(stmt)

    if agent:
        return AgentSchema().dump(agent)
    else:
        return {"error": "Agent not found"}, 404


# create agent
@agents_bp.route("/", methods=["POST"])
@jwt_required()  # Get the JSON web token from the user as users must be logged in to add a review
def create_agent():
    admin_required()

    agent_info = AgentSchema().load(request.json)
    agent = Agent(
        name=agent_info["name"],
        email=agent_info["email"],
        contact_number=agent_info["contact_number"],
        overview=agent_info["overview"],
        languages=agent_info["languages"],
    )
    db.session.add(agent)
    db.session.commit()

    return AgentSchema().dump(agent), 201


# Update a agent - change name, email, or password
@agents_bp.route("/<int:agent_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_agent(agent_id):
    agent = Agent.query.get(agent_id)

    if agent:
        admin_required()
        agent_info = AgentSchema().load(request.json, partial=True)
        agent.name = agent_info.get("name", agent.name)
        agent.email = agent_info.get("email", agent.email)
        agent.contact_number = agent_info.get("contact_number", agent.contact_number)
        agent.overview = agent_info.get("overview", agent.overview)
        agent.languages = agent_info.get("languages", agent.languages)

        db.session.commit()
        return AgentSchema().dump(agent)
    else:
        return {"error": "Agent not found"}, 404


# Delete a agent - only admins can do this
@agents_bp.route("/<int:agent_id>", methods=["DELETE"])
@jwt_required()
def delete_agent(agent_id):
    agent = Agent.query.get(agent_id)

    if agent:
        admin_required()
        db.session.delete(agent)
        db.session.commit()
        return {"message": f"Agent {agent.name} deleted successfully"}, 200
    else:
        return {"error": "Agent not found"}, 404
