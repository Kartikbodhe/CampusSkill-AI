import os
from flask import Flask, render_template
from config import config_by_name
from extensions import db, login_manager
from utils.security import get_or_create_csrf_token


def create_app(config_name=None):
    """Application factory for CampusSkill AI."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models.user import User
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Context processors for global template variables
    @app.context_processor
    def inject_global_template_vars():
        return {
            "csrf_token": get_or_create_csrf_token(),
            "current_year": 2026,
            "app_name": "CampusSkill AI",
        }

    # Register Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        msg = getattr(error, "description", "Bad Request")
        return render_template("errors/error.html", code=400, title="Bad Request", message=msg), 400

    @app.errorhandler(403)
    def forbidden(error):
        msg = getattr(error, "description", "You do not have permission to view this page.")
        return render_template("errors/error.html", code=403, title="Forbidden", message=msg), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/error.html", code=404, title="Page Not Found", message="The requested URL was not found on this server."), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/error.html", code=500, title="Internal Server Error", message="An unexpected error occurred. Please try again later."), 500

    # Register all application blueprints
    from routes import (
        main_bp,
        auth_bp,
        student_bp,
        skills_bp,
        analyzer_bp,
        roadmap_bp,
        assessments_bp,
        placement_bp,
        admin_bp,
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(assessments_bp)
    app.register_blueprint(placement_bp)
    app.register_blueprint(admin_bp)

    # Auto-initialize database tables and seed sample records
    with app.app_context():
        db.create_all()
        # Seed initial data if skills table is empty
        from models.skills import Skill
        if Skill.query.count() == 0:
            from services.seed_data import seed_database
            seed_database()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)