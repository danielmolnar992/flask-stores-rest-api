import os

import redis
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from rq import Queue

from blocklist import BLOCKLIST
from db import db
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv('.env', verbose=True)

    connection = redis.from_url(os.getenv('REDIS_URL'))
    app.queue = Queue('emails', connection=connection)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = \
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = \
        db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate = Migrate(app, db)  # noqa F841
    api = Api(app)

    # use secrets.SystemRandom().getrandbits(128)
    # but shouldn't change with every restart
    # add import secrets if needed
    app.config['JWT_SECRET_KEY'] = '208125270422126691855768048905400260971'
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        """If returns true, terminates the request. Error message defined
        in revoked_token_loader. Logout puts the token in the blocklist."""
        return jwt_payload['jti'] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Error message returned when token is in blocklist."""
        return (
            jsonify({'description': 'The token has been revoked.',
                     'error': 'token_revoked'}),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        """When requires a fresh access token, but gets a non-fresh one."""
        return (
            jsonify(
                {'description': 'The token is not fresh.',
                 'error': 'fresh_token_required'}),
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        """Check item delete endpoint for usage"""
        # Read from a config file instead of hard-coding
        if identity == 1:
            return {'is_admin': True}
        return {'is_admin': False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Error for expired tokens in the requiest."""
        return (
            jsonify(
                {'message': 'The token has expired.',
                 'error': 'token_expired'}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Error for invalid tokens in the request."""
        return (
            jsonify(
                {'message': 'Signature veridication failed.',
                 'error': 'invalid_token'}),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Error for missing token from the request."""
        return (
            jsonify({'description': 'Request does not conatin an access token',
                     'error': 'authorization_required'}),
            401
        )

    # before first request replacement was removed once
    # Migrate(app, db) was added, Flask-Migrate doesn it for us
    # import models
    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
