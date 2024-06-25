from flask import Flask
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from init import db, ma, bcrypt, jwt
from blueprints.cli_bp import db_commands
from blueprints.users_bp import users_bp
from blueprints.agents_bp import agents_bp
from blueprints.auth_bp import auth_bp
from blueprints.testimonials_bp import testimonials_bp
from blueprints.appointments_bp import appointments_bp

def create_app():
    app = Flask(__name__)
        
        
    @app.errorhandler(404)
    def not_found(err):
        return {"error": "Not Found"}, 404


    @app.errorhandler(ValidationError)
    def invalid_request(err):
        return {"error": vars(err)["messages"]}, 400

    @app.errorhandler(ValueError)
    def invalid_data(err):
        return {"error": str(err)}, 400

    @app.errorhandler(KeyError)
    def missing_key(err):
        return {"error": f"Missing field: {str(err)}"}, 400
    
    @app.errorhandler(IntegrityError)
    def integrity_error(err):
        return {"error": str(err)}, 409
    
    @app.errorhandler(PermissionError)
    def permission_error(err):
        return {"error": str(err)}, 403
    
    @app.errorhandler(Exception)
    def unhandled_exception(err):
        return {"error": str(err)}, 500


    app.config.from_object('config.app_config')


    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(db_commands)
    app.register_blueprint(users_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(testimonials_bp)
    app.register_blueprint(appointments_bp)


    return app
