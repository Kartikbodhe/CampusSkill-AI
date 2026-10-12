import pytest
from app import create_app
from extensions import db
from models.user import User, StudentProfile
from services.seed_data import seed_database


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_password_hashing(app):
    with app.app_context():
        user = User(email="test_hash@example.com", role="student")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "SecurePass123!"
        assert user.check_password("SecurePass123!") is True
        assert user.check_password("WrongPassword") is False


def test_registration_success(client, app):
    response = client.post("/register", data={
        "full_name": "New Student",
        "email": "newstudent@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
        "branch": "Computer Science",
        "current_year": "3rd Year"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        u = User.query.filter_by(email="newstudent@example.com").first()
        assert u is not None
        assert u.role == "student"
        assert u.student_profile is not None
        assert u.student_profile.full_name == "New Student"


def test_registration_duplicate_email(client, app):
    response = client.post("/register", data={
        "full_name": "Duplicate Student",
        "email": "student@campusskill.edu",  # seeded email
        "password": "Password123",
        "confirm_password": "Password123",
        "branch": "Computer Science",
        "current_year": "3rd Year"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"already exists" in response.data


def test_login_valid_and_invalid(client):
    # Invalid password
    bad_resp = client.post("/login", data={
        "email": "student@campusskill.edu",
        "password": "WrongPassword"
    }, follow_redirects=True)
    assert b"Invalid email or password" in bad_resp.data

    # Valid login
    good_resp = client.post("/login", data={
        "email": "student@campusskill.edu",
        "password": "Student@123"
    }, follow_redirects=True)
    assert good_resp.status_code == 200
    assert b"Rahul Sharma" in good_resp.data
