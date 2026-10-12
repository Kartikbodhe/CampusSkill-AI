import pytest
from app import create_app
from extensions import db
from models.user import User
from services.seed_data import seed_database
from services.readiness import calculate_placement_readiness, DEFAULT_WEIGHTS


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.drop_all()


def test_placement_readiness_calculator(app):
    with app.app_context():
        user = User.query.filter_by(email="student@campusskill.edu").first()
        profile = user.student_profile

        readiness = calculate_placement_readiness(profile)
        assert readiness is not None
        assert "overall_score" in readiness
        assert 0.0 <= readiness["overall_score"] <= 100.0
        assert "band" in readiness
        assert "breakdown" in readiness
        assert "technical" in readiness["breakdown"]
        assert "aptitude" in readiness["breakdown"]
        assert "dsa" in readiness["breakdown"]
        assert "communication" in readiness["breakdown"]
        assert "assessment" in readiness["breakdown"]

        # Sum of configurable weights must be 1.0
        assert round(sum(DEFAULT_WEIGHTS.values()), 2) == 1.0


def test_readiness_custom_weights(app):
    with app.app_context():
        user = User.query.filter_by(email="student@campusskill.edu").first()
        profile = user.student_profile

        custom_weights = {
            "technical": 0.60,
            "aptitude": 0.10,
            "dsa": 0.10,
            "communication": 0.10,
            "assessment": 0.10,
        }

        readiness = calculate_placement_readiness(profile, weights=custom_weights)
        assert readiness["breakdown"]["technical"]["weight_percent"] == 60
