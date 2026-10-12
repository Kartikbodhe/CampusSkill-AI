from routes.main import main_bp
from routes.auth import auth_bp
from routes.student import student_bp
from routes.skills import skills_bp
from routes.analyzer import analyzer_bp
from routes.roadmap import roadmap_bp
from routes.assessments import assessments_bp
from routes.placement import placement_bp
from routes.admin import admin_bp

__all__ = [
    "main_bp",
    "auth_bp",
    "student_bp",
    "skills_bp",
    "analyzer_bp",
    "roadmap_bp",
    "assessments_bp",
    "placement_bp",
    "admin_bp",
]
