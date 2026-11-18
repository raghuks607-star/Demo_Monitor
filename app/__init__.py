"""Demo Monitoring Infrastructure — Flask application factory."""

from flask import Flask
from flask_wtf import CSRFProtect

from app.config import Config

csrf = CSRFProtect()


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask app for local demo use."""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    csrf.init_app(app)

    from app.db import init_app as init_db_app

    init_db_app(app)

    from app.routes import bp

    app.register_blueprint(bp)

    @app.context_processor
    def inject_auth():
        from app.auth import current_user

        return {"current_user": current_user()}

    return app
