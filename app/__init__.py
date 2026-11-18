import logging
from flask import Flask, render_template
from app.config import Config
from app.models import db
from app.routes import main_bp
from app.database import initialize_database

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
)


def create_app(config_class=Config) -> Flask:
    """Application factory for the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database extensions
    db.init_app(app)

    # Register application routes
    app.register_blueprint(main_bp)

    # Auto-initialize tables and seed data if connected
    initialize_database(app)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template(
            "index.html",
            db_status={
                "connected": False,
                "latency_ms": None,
                "dialect": "Unknown",
                "version": None,
                "error": str(e),
            },
            diagnostics={},
            items=[],
            item_count=0,
        ), 500

    return app
