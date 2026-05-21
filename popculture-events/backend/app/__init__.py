from flask import Flask

from app.blueprints import register_blueprints
from app.commands import register_commands
from app.config import Config
from app.errors import register_error_handlers
from app.extensions import cors, db, jwt, migrate


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.json.ensure_ascii = False

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "supports_credentials": True,
            }
        },
    )

    with app.app_context():
        from app import models

    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)

    return app