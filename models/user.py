from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """User account model supporting multiple roles."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="student")  # 'student', 'placement_officer', 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # One-to-one relationship with StudentProfile
    student_profile = db.relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and store the password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password hash against user input."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_student(self):
        return self.role == "student"

    @property
    def is_placement_officer(self):
        return self.role == "placement_officer"

    @property
    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class StudentProfile(db.Model):
    """Profile details for registered students."""
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    college_name = db.Column(db.String(150), nullable=True, default="Engineering Institute of Technology")
    branch = db.Column(db.String(80), nullable=False, default="Computer Science")
    current_year = db.Column(db.String(20), nullable=False, default="3rd Year")
    graduation_year = db.Column(db.Integer, nullable=True, default=2026)
    career_objective = db.Column(db.Text, nullable=True)
    
    # Target Job Role reference
    target_job_role_id = db.Column(db.Integer, db.ForeignKey("job_roles.id", ondelete="SET NULL"), nullable=True)

    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="student_profile")
    target_job_role = db.relationship("JobRole")
    skills = db.relationship("StudentSkill", back_populates="student_profile", cascade="all, delete-orphan")
    assessment_attempts = db.relationship("AssessmentAttempt", back_populates="student_profile", cascade="all, delete-orphan")
    roadmaps = db.relationship("Roadmap", back_populates="student_profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StudentProfile {self.full_name} ({self.branch})>"
