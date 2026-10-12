from datetime import datetime, timezone
from extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Assessment(db.Model):
    """Test modules for evaluating student competencies."""
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'Technical', 'SQL', 'Python', 'Aptitude', 'DSA', 'Communication'
    description = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=15)
    passing_score = db.Column(db.Float, nullable=False, default=60.0)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    questions = db.relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    attempts = db.relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assessment {self.title} ({self.category})>"


class Question(db.Model):
    """Multiple choice practice question with rationale."""
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    explanation = db.Column(db.Text, nullable=True)

    # Relationships
    assessment = db.relationship("Assessment", back_populates="questions")
    answers = db.relationship("AssessmentAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question id={self.id} assessment_id={self.assessment_id}>"


class AssessmentAttempt(db.Model):
    """Completed assessment record with performance metrics."""
    __tablename__ = "assessment_attempts"

    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Float, nullable=False)  # Percentage 0.0 - 100.0
    total_questions = db.Column(db.Integer, nullable=False)
    correct_count = db.Column(db.Integer, nullable=False)
    passed = db.Column(db.Boolean, nullable=False)
    time_taken_seconds = db.Column(db.Integer, nullable=True, default=0)
    attempted_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    student_profile = db.relationship("StudentProfile", back_populates="assessment_attempts")
    assessment = db.relationship("Assessment", back_populates="attempts")
    answers = db.relationship("AssessmentAnswer", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AssessmentAttempt id={self.id} student={self.student_profile_id} score={self.score}%>"


class AssessmentAnswer(db.Model):
    """Student answer detail for auditing and feedback."""
    __tablename__ = "assessment_answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option = db.Column(db.String(1), nullable=True)  # 'A', 'B', 'C', 'D'
    is_correct = db.Column(db.Boolean, nullable=False)

    # Relationships
    attempt = db.relationship("AssessmentAttempt", back_populates="answers")
    question = db.relationship("Question", back_populates="answers")

    def __repr__(self):
        return f"<AssessmentAnswer attempt={self.attempt_id} q={self.question_id} correct={self.is_correct}>"
