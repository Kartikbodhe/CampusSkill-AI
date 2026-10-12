import pytest
from app import create_app
from extensions import db
from models.user import User
from models.jobs import JobRole
from models.skills import Skill, StudentSkill
from services.seed_data import seed_database
from services.skill_gap import analyze_skill_gap


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.drop_all()


def test_skill_gap_calculation(app):
    with app.app_context():
        user = User.query.filter_by(email="student@campusskill.edu").first()
        profile = user.student_profile
        da_role = JobRole.query.filter_by(title="Data Analyst").first()

        gap = analyze_skill_gap(profile, da_role)
        assert gap is not None
        assert "match_percentage" in gap
        assert gap["match_percentage"] >= 0.0
        assert gap["match_percentage"] <= 100.0
        assert gap["total_required_skills"] > 0
        assert gap["earned_weight"] <= gap["total_possible_weight"]

        # Check categorization
        missing_names = [m["skill_name"] for m in gap["missing_skills"]]
        assert "Power BI" in missing_names  # Rahul hasn't recorded Power BI initially


def test_gap_analysis_regeneration_on_skill_add(app):
    with app.app_context():
        user = User.query.filter_by(email="student@campusskill.edu").first()
        profile = user.student_profile
        da_role = JobRole.query.filter_by(title="Data Analyst").first()

        initial_gap = analyze_skill_gap(profile, da_role)
        initial_score = initial_gap["match_percentage"]

        # Student learns Power BI to Advanced
        power_bi = Skill.query.filter_by(name="Power BI").first()
        new_ss = StudentSkill(
            student_profile_id=profile.id,
            skill_id=power_bi.id,
            proficiency_level="advanced"
        )
        db.session.add(new_ss)
        db.session.commit()

        # Regenerate analysis
        updated_gap = analyze_skill_gap(profile, da_role)
        assert updated_gap["match_percentage"] > initial_score
        assert "Power BI" not in [m["skill_name"] for m in updated_gap["missing_skills"]]
