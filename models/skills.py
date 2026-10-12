from datetime import datetime, timezone
from extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Skill(db.Model):
    """Catalog of technical and professional skills."""
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default="Technical")
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    student_skills = db.relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")
    job_role_skills = db.relationship("JobRoleSkill", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill {self.name} ({self.category})>"


class StudentSkill(db.Model):
    """Associative model linking students to their recorded skills and proficiency."""
    __tablename__ = "student_skills"

    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    
    # Proficiency: 'beginner', 'intermediate', 'advanced'
    proficiency_level = db.Column(db.String(20), nullable=False, default="beginner")
    
    # Assessment-based validation score (0 - 100), if tested
    assessment_score = db.Column(db.Float, nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("student_profile_id", "skill_id", name="uq_student_skill"),
    )

    # Relationships
    student_profile = db.relationship("StudentProfile", back_populates="skills")
    skill = db.relationship("Skill", back_populates="student_skills")

    @property
    def numeric_level(self):
        """Map proficiency string to numerical weight: beginner=1, intermediate=2, advanced=3."""
        mapping = {"beginner": 1, "intermediate": 2, "advanced": 3}
        return mapping.get(self.proficiency_level.lower(), 1)

    def __repr__(self):
        return f"<StudentSkill student_id={self.student_profile_id} skill={self.skill_id} lvl={self.proficiency_level}>"
