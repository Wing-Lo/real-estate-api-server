from datetime import date
from flask import Blueprint
from models.user import User
from models.agent import Agent
from models.testimonial import Testimonial
from models.appointment import Appointment
from init import db, bcrypt

# Define blueprint for database commands
db_commands = Blueprint('db', __name__)

# Command to create tables in the database
@db_commands.cli.command('create')
def create_db():
    db.drop_all()  # Drop existing tables
    db.create_all()  # Create tables based on defined models
    print('Tables created')

# Command to seed initial data into the database
@db_commands.cli.command('seed')
def seed_db():
    # Create initial users
    users = [
        User(
            name='Administrator',
            email='admin@test.com',
            contact_number='0433222111',
            password=bcrypt.generate_password_hash('admin1234').decode('utf-8'),
            is_admin=True
        ),
        User(
            name='Gary Johnson',
            email='garyjohnson@test.com',
            contact_number='0411223344',
            password=bcrypt.generate_password_hash('gjgj1234').decode('utf-8')
        ),
        User(
            name='Lucas Smith',
            email='lucassmith@test.com',
            contact_number='0411333444',
            password=bcrypt.generate_password_hash('lsls1234').decode('utf-8')
        ),
        User(
            name='Leo Benjamin',
            email='leobenjamin@test.com',
            contact_number='0422333444',
            password=bcrypt.generate_password_hash('lblb1234').decode('utf-8')
        ),
        User(
            name='Thomas Franklin',
            email='thomasfranklin@test.com',
            contact_number='0411333444',
            password=bcrypt.generate_password_hash('tftf1234').decode('utf-8')
        )
    ]

    # Add users to session and commit to database
    db.session.add_all(users)
    db.session.commit()

    # Create initial agents
    agents = [
        Agent(
            name='Peter Richard',
            email='peterrichard@agent.com',
            contact_number='0411555666',
            overview='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            languages=['Korean', 'French']
        ),
        Agent(
            name='Emily White',
            email='emilywhite@agent.com',
            contact_number='0411666777',
            overview='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            languages=['Mandarin', 'Cantonese']
        ),
        Agent(
            name='Stephen Green',
            email='stephengreen@agent.com',
            contact_number='0411888777',
            overview='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            languages=['Japanese', 'Cantonese']
        ),
        Agent(
            name='Ana Simpson',
            email='anasimpson@agent.com',
            contact_number='0411666888',
            overview='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            languages=['Spanish', 'French']
        ),
        Agent(
            name='Dennis Christopher',
            email='dennischristopher@agent.com',
            contact_number='0433000999',
            overview='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            languages=['Korean', 'Japanese']
        )
    ]

    # Add agents to session and commit to database
    db.session.add_all(agents)
    db.session.commit()

    # Create initial testimonials
    testimonials = [
        Testimonial(
            property_address='33 Main Street, Brisbane QLD 4000',
            comment='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            rating=5,
            date_created=date.today(),
            user_id=users[1].id,
            agent_id=agents[2].id
        ),
        Testimonial(
            property_address='28 Hello Street, Brisbane QLD 4000',
            comment='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            rating=4,
            date_created=date.today(),
            user_id=users[2].id,
            agent_id=agents[1].id
        ),
        Testimonial(
            property_address='12 World Street, Brisbane QLD 4000',
            comment='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            rating=5,
            date_created=date.today(),
            user_id=users[3].id,
            agent_id=agents[4].id
        ),
        Testimonial(
            property_address='9 Dream Street, Brisbane QLD 4000',
            comment='Lorem Ipsum is simply dummy information and therefore cannot be used in real life.',
            rating=5,
            date_created=date.today(),
            user_id=users[1].id,
            agent_id=agents[3].id
        )
    ]

    # Add testimonials to session and commit to database
    db.session.add_all(testimonials)
    db.session.commit()

    # Create initial appointments
    appointments = [
        Appointment(
            date='2024-8-3',
            time='10:15:00',
            agent_id=1,
            user_id=1,
        ),
        Appointment(
            date='2024-9-4',
            time='10:30:00',
            agent_id=1,
            user_id=2,
        ),
        Appointment(
            date='2024-11-2',
            time='10:45:00',
            agent_id=3,
            user_id=3,
        ),
        Appointment(
            date='2024-11-12',
            time='10:00:00',
            agent_id=2,
            user_id=4,
        ),
        Appointment(
            date='2024-12-3',
            time='10:30:00',
            agent_id=4,
            user_id=5,
        )
    ]

    # Add appointments to session and commit to database
    db.session.add_all(appointments)
    db.session.commit()

    print('Tables seeded')  # Confirmation message after seeding
