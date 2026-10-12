from datetime import datetime, timezone
from extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class JobRole(db.Model):
    """Job role catalog with skill requirements and industry preparation pathways."""
    __tablename__ = "job_roles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False, default="Software Engineering")
    description = db.Column(db.Text, nullable=False)
    salary_range = db.Column(db.String(80), nullable=True, default="₹6 LPA - ₹14 LPA (Sample)")
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    role_skills = db.relationship("JobRoleSkill", back_populates="job_role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JobRole {self.title}>"


class JobRoleSkill(db.Model):
    """Associative model defining skill requirements, importance weights, and target levels."""
    __tablename__ = "job_role_skills"

    id = db.Column(db.Integer, primary_key=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    
    # Weight: 1 (Optional/Good-to-have), 2 (Important), 3 (Critical/High Priority)
    importance_weight = db.Column(db.Integer, nullable=False, default=2)
    min_proficiency = db.Column(db.String(20), nullable=False, default="intermediate")  # 'beginner', 'intermediate', 'advanced'
    is_required = db.Column(db.Boolean, nullable=False, default=True)
    recommendation_tip = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("job_role_id", "skill_id", name="uq_job_role_skill"),
    )

    # Relationships
    job_role = db.relationship("JobRole", back_populates="role_skills")
    skill = db.relationship("Skill", back_populates="job_role_skills")

    @property
    def numeric_target(self):
        mapping = {"beginner": 1, "intermediate": 2, "advanced": 3}
        return mapping.get(self.min_proficiency.lower(), 2)

    def __repr__(self):
        return f"<JobRoleSkill role={self.job_role_id} skill={self.skill_id} weight={self.importance_weight}>"
