from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.agent import Agent, AgentSchema  # Import Agent model and schema
from init import db
from blueprints.auth_bp import admin_required  # Import admin_required decorator

agents_bp = Blueprint("agents", __name__, url_prefix="/agents")  # Define Blueprint for agents

# Get all agents
@agents_bp.route("/", methods=["GET"])
@jwt_required()  # JWT token required for authentication
def get_all_agents():
    stmt = db.select(Agent).order_by(Agent.id)  # SQLAlchemy select statement for all agents
    agents = db.session.scalars(stmt).all()  # Execute the statement and fetch all agents

    if not agents:
        return {"error": "Agents not found"}, 404  # Return error if no agents found

    return AgentSchema(many=True).dump(agents)  # Serialize agents to JSON using AgentSchema


# Retrieve one agent by ID
@agents_bp.route("/<int:agent_id>", methods=["GET"])
@jwt_required()  # JWT token required for authentication
def get_one_agent(agent_id):
    stmt = db.select(Agent).filter_by(id=agent_id)  # SQLAlchemy select statement for specific agent by ID
    agent = db.session.scalar(stmt)  # Execute the statement and fetch the agent

    if agent:
        return AgentSchema().dump(agent)  # Serialize agent to JSON using AgentSchema
    else:
        return {"error": "Agent not found"}, 404  # Return error if agent with given ID not found


# Create a new agent
@agents_bp.route("/", methods=["POST"])
@jwt_required()  # JWT token required for authentication
def create_agent():
    admin_required()  # Ensure user is admin

    agent_info = AgentSchema().load(request.json)  # Deserialize request JSON to AgentSchema
    agent = Agent(  # Create new Agent object
        name=agent_info["name"],
        email=agent_info["email"],
        contact_number=agent_info["contact_number"],
        overview=agent_info["overview"],
        languages=agent_info["languages"],
    )
    db.session.add(agent)  # Add agent to session
    db.session.commit()  # Commit changes to database

    return AgentSchema().dump(agent), 201  # Serialize agent to JSON and return with HTTP status code 201


# Update an agent by ID
@agents_bp.route("/<int:agent_id>", methods=["PUT", "PATCH"])
@jwt_required()  # JWT token required for authentication
def update_agent(agent_id):
    agent = Agent.query.get(agent_id)  # Retrieve agent by ID

    if agent:
        admin_required()  # Ensure user is admin
        agent_info = AgentSchema().load(request.json, partial=True)  # Deserialize request JSON to AgentSchema (partial update)
        agent.name = agent_info.get("name", agent.name)  # Update agent attributes
        agent.email = agent_info.get("email", agent.email)
        agent.contact_number = agent_info.get("contact_number", agent.contact_number)
        agent.overview = agent_info.get("overview", agent.overview)
        agent.languages = agent_info.get("languages", agent.languages)

        db.session.commit()  # Commit changes to database
        return AgentSchema().dump(agent)  # Serialize updated agent to JSON and return
    else:
        return {"error": "Agent not found"}, 404  # Return error if agent with given ID not found


# Delete an agent by ID
@agents_bp.route("/<int:agent_id>", methods=["DELETE"])
@jwt_required()  # JWT token required for authentication
def delete_agent(agent_id):
    agent = Agent.query.get(agent_id)  # Retrieve agent by ID

    if agent:
        admin_required()  # Ensure user is admin
        db.session.delete(agent)  # Delete agent from database
        db.session.commit()  # Commit changes

        return {"message": f"Agent {agent.name} deleted successfully"}, 200  # Return success message
    else:
        return {"error": "Agent not found"}, 404  # Return error if agent with given ID not found
