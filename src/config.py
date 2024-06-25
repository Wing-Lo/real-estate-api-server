import os

class Config(object):
    # Secret key for JWT, fetched from environment variables
    JWT_SECRET_KEY = os.environ.get('JWT_KEY')
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        # Fetch the database URI from environment variables
        value = os.environ.get('DB_URI')
        if not value:
            # Raise an error if the database URI is not set
            raise ValueError('DATABASE_URI is not set')
        return value
    
class DevelopmentConfig(Config):
    # Enable debugging in development environment
    DEBUG = True

class ProductionConfig(Config):
    # Production-specific configurations (currently none)
    pass

class TestingConfig(Config):
    # Enable testing mode
    TESTING = True

# Determine the environment and set the corresponding configuration
environment = os.environ.get("FLASK_ENV")
if environment == "production":
    app_config = ProductionConfig()
elif environment == "testing":
    app_config = TestingConfig()
else:
    app_config = DevelopmentConfig()