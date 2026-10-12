from datetime import datetime, timezone
from extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Roadmap(db.Model):
    """Personalized learning journey based on identified skill gaps."""
    __tablename__ = "roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    target_job_role_id = db.Column(db.Integer, db.ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False)
    completion_percentage = db.Column(db.Float, nullable=False, default=0.0)
    generated_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    student_profile = db.relationship("StudentProfile", back_populates="roadmaps")
    target_job_role = db.relationship("JobRole")
    tasks = db.relationship("RoadmapTask", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapTask.phase, RoadmapTask.id")

    def recalculate_completion(self):
        """Recalculate and update completion percentage."""
        if not self.tasks:
            self.completion_percentage = 0.0
            return 0.0
        completed = sum(1 for t in self.tasks if t.is_completed)
        self.completion_percentage = round((completed / len(self.tasks)) * 100.0, 1)
        return self.completion_percentage

    def __repr__(self):
        return f"<Roadmap student={self.student_profile_id} role={self.target_job_role_id} {self.completion_percentage}%>"


class RoadmapTask(db.Model):
    """Actionable milestone inside a learning roadmap."""
    __tablename__ = "roadmap_tasks"

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(60), nullable=False, default="Technical")
    
    # Phase: 1 (Fundamentals), 2 (Practical Exercises), 3 (Mini-Projects), 4 (Interview Prep)
    phase = db.Column(db.Integer, nullable=False, default=1)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="High")  # 'High', 'Medium', 'Low'
    estimated_hours = db.Column(db.Integer, nullable=False, default=6)
    resource_url = db.Column(db.String(255), nullable=True)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    roadmap = db.relationship("Roadmap", back_populates="tasks")

    @property
    def phase_title(self):
        phases = {
            1: "Phase 1: Core Fundamentals",
            2: "Phase 2: Practical Exercises",
            3: "Phase 3: Mini-Projects",
            4: "Phase 4: Interview Preparation"
        }
        return phases.get(self.phase, f"Phase {self.phase}")

    def __repr__(self):
        return f"<RoadmapTask id={self.id} title={self.title} phase={self.phase} done={self.is_completed}>"
