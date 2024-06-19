from init import db
from flask import Blueprint, request
from models.agent import Agent, AgentSchema
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError


agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

# Get all agents
@agents_bp.route('/', methods=['GET'])
def all_agents():
    stmt = db.select(Agent).order_by(Agent.id) 
    agents = db.session.scalars(stmt).all() 
    return AgentSchema(many=True).dump(agents) 

# Retrieve one agent
@agents_bp.route('/<int:agent_id>', methods=['GET'])
def one_agent(agent_id):
    stmt = db.select(Agent).filter_by(id=agent_id)
    agent = db.session.scalar(stmt) 
    if agent: 
        return AgentSchema().dump(agent)
    else:
        return {'error':'Agent not found'}, 404 