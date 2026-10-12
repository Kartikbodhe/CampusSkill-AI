import pytest
from app import create_app
from extensions import db
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


def test_unauthenticated_redirection(client):
    # Student dashboard requires login
    response = client.get("/student/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # Placement dashboard requires login
    p_resp = client.get("/placement/dashboard", follow_redirects=False)
    assert p_resp.status_code == 302
    assert "/login" in p_resp.headers["Location"]


def test_student_cannot_access_admin_or_placement(client):
    # Log in as student
    client.post("/login", data={
        "email": "student@campusskill.edu",
        "password": "Student@123"
    })

    # Try accessing placement dashboard -> should be 403 Forbidden
    resp_placement = client.get("/placement/dashboard")
    assert resp_placement.status_code == 403

    # Try accessing admin dashboard -> should be 403 Forbidden
    resp_admin = client.get("/admin/dashboard")
    assert resp_admin.status_code == 403


def test_placement_officer_access(client):
    # Log in as placement officer
    client.post("/login", data={
        "email": "placement@campusskill.edu",
        "password": "Placement@123"
    })

    resp = client.get("/placement/dashboard")
    assert resp.status_code == 200
    assert b"Cohort Placement Intelligence" in resp.data

    # Placement officer cannot access admin dashboard
    admin_resp = client.get("/admin/dashboard")
    assert admin_resp.status_code == 403


def test_admin_access(client):
    # Log in as administrator
    client.post("/login", data={
        "email": "admin@campusskill.edu",
        "password": "Admin@123"
    })

    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    assert b"Platform Administration Console" in resp.data
