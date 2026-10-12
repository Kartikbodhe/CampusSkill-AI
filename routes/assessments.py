from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.assessments import Assessment, Question, AssessmentAttempt, AssessmentAnswer
from models.skills import Skill, StudentSkill
from models.audit import AuditLog
from utils.security import role_required, csrf_protect

assessments_bp = Blueprint("assessments", __name__, url_prefix="/assessments")


@assessments_bp.route("/", methods=["GET"])
@login_required
@role_required("student")
def list_assessments():
    profile = current_user.student_profile
    assessments = Assessment.query.order_by(Assessment.category).all()
    
    # Map student's highest scores per assessment
    attempts = AssessmentAttempt.query.filter_by(student_profile_id=profile.id).all()
    best_scores = {}
    for att in attempts:
        if att.assessment_id not in best_scores or att.score > best_scores[att.assessment_id]:
            best_scores[att.assessment_id] = att.score

    history = AssessmentAttempt.query.filter_by(
        student_profile_id=profile.id
    ).order_by(AssessmentAttempt.attempted_at.desc()).limit(10).all()

    return render_template(
        "assessments/index.html",
        assessments=assessments,
        best_scores=best_scores,
        history=history,
        profile=profile
    )


@assessments_bp.route("/<int:assessment_id>/take", methods=["GET"])
@login_required
@role_required("student")
def take_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    questions = assessment.questions
    if not questions:
        flash("No questions currently assigned to this test module.", "warning")
        return redirect(url_for("assessments.list_assessments"))

    return render_template(
        "assessments/take.html",
        assessment=assessment,
        questions=questions
    )


@assessments_bp.route("/<int:assessment_id>/submit", methods=["POST"])
@login_required
@role_required("student")
@csrf_protect
def submit_assessment(assessment_id):
    profile = current_user.student_profile
    assessment = Assessment.query.get_or_404(assessment_id)
    questions = assessment.questions

    total_q = len(questions)
    if total_q == 0:
        flash("Empty assessment.", "danger")
        return redirect(url_for("assessments.list_assessments"))

    correct_count = 0
    time_taken = int(request.form.get("time_taken_seconds", 0))

    attempt = AssessmentAttempt(
        student_profile_id=profile.id,
        assessment_id=assessment.id,
        total_questions=total_q,
        correct_count=0,
        score=0.0,
        passed=False,
        time_taken_seconds=time_taken,
        attempted_at=datetime.now(timezone.utc)
    )
    db.session.add(attempt)
    db.session.flush()

    answer_records = []
    for q in questions:
        selected = request.form.get(f"q_{q.id}", "").strip().upper()
        is_correct = (selected == q.correct_option)
        if is_correct:
            correct_count += 1

        ans_entry = AssessmentAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=selected if selected in ["A", "B", "C", "D"] else None,
            is_correct=is_correct
        )
        answer_records.append(ans_entry)

    db.session.add_all(answer_records)

    score_pct = round((correct_count / total_q) * 100.0, 1)
    attempt.correct_count = correct_count
    attempt.score = score_pct
    attempt.passed = (score_pct >= assessment.passing_score)

    # If student has a matching skill in their profile, mark verified assessment score!
    matching_skill = Skill.query.filter(
        (Skill.name.ilike(f"%{assessment.category}%")) |
        (Skill.category.ilike(f"%{assessment.category}%"))
    ).first()
    if matching_skill:
        st_skill = StudentSkill.query.filter_by(
            student_profile_id=profile.id,
            skill_id=matching_skill.id
        ).first()
        if st_skill:
            st_skill.assessment_score = max(st_skill.assessment_score or 0.0, score_pct)
            if attempt.passed:
                st_skill.verified = True

    db.session.commit()
    AuditLog.log("ASSESSMENT_COMPLETED", user_id=current_user.id, details=f"Attempted {assessment.title} - Score: {score_pct}%")

    flash(f"Assessment completed! Your score: {score_pct}%.", "success" if attempt.passed else "info")
    return redirect(url_for("assessments.view_result", attempt_id=attempt.id))


@assessments_bp.route("/attempt/<int:attempt_id>", methods=["GET"])
@login_required
@role_required("student")
def view_result(attempt_id):
    profile = current_user.student_profile
    attempt = AssessmentAttempt.query.get_or_404(attempt_id)

    # Check ownership
    if attempt.student_profile_id != profile.id:
        flash("Unauthorized result view.", "danger")
        return redirect(url_for("assessments.list_assessments"))

    return render_template(
        "assessments/result.html",
        attempt=attempt,
        assessment=attempt.assessment,
        answers=attempt.answers
    )
