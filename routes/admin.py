from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.skills import Skill
from models.jobs import JobRole, JobRoleSkill
from models.assessments import Assessment, Question
from models.audit import AuditLog
from utils.security import role_required, csrf_protect

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@role_required("admin")
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    roles = JobRole.query.order_by(JobRole.title).all()
    assessments = Assessment.query.all()
    questions_count = Question.query.count()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(25).all()

    stats = {
        "total_users": len(users),
        "total_students": sum(1 for u in users if u.is_student),
        "total_placement_officers": sum(1 for u in users if u.is_placement_officer),
        "total_job_roles": len(roles),
        "total_assessments": len(assessments),
        "total_questions": questions_count,
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        users=users,
        roles=roles,
        assessments=assessments,
        audit_logs=audit_logs
    )


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@role_required("admin")
@csrf_protect
def toggle_user_status(user_id):
    if user_id == current_user.id:
        flash("You cannot deactivate your own administrative account.", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()

    action_label = "Activated" if user.is_active else "Deactivated"
    AuditLog.log("USER_STATUS_TOGGLED", user_id=current_user.id, details=f"{action_label} user {user.email}")
    flash(f"Account for {user.email} is now {action_label.lower()}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/change-role", methods=["POST"])
@login_required
@role_required("admin")
@csrf_protect
def change_user_role(user_id):
    if user_id == current_user.id:
        flash("You cannot modify your own administrative role.", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")
    if new_role in ["student", "placement_officer", "admin"]:
        old_role = user.role
        user.role = new_role
        db.session.commit()
        AuditLog.log("USER_ROLE_CHANGED", user_id=current_user.id, details=f"Changed {user.email} from {old_role} to {new_role}")
        flash(f"Updated role for {user.email} to {new_role}.", "success")
    else:
        flash("Invalid role selected.", "danger")

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/jobs/create", methods=["POST"])
@login_required
@role_required("admin")
@csrf_protect
def create_job_role():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "Software Engineering").strip()
    description = request.form.get("description", "").strip()
    salary_range = request.form.get("salary_range", "₹6 LPA - ₹12 LPA").strip()

    if not title or not description:
        flash("Role title and description are required.", "danger")
        return redirect(url_for("admin.dashboard"))

    existing = JobRole.query.filter_by(title=title).first()
    if existing:
        flash(f"Job role '{title}' already exists.", "warning")
        return redirect(url_for("admin.dashboard"))

    new_role = JobRole(title=title, category=category, description=description, salary_range=salary_range)
    db.session.add(new_role)
    db.session.commit()

    AuditLog.log("JOB_ROLE_CREATED", user_id=current_user.id, details=f"Created job role {title}")
    flash(f"Created job role '{title}' successfully.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/jobs/<int:job_id>/add-skill", methods=["POST"])
@login_required
@role_required("admin")
@csrf_protect
def add_job_role_skill(job_id):
    job_role = JobRole.query.get_or_404(job_id)
    skill_id = request.form.get("skill_id")
    weight = request.form.get("importance_weight", "2")
    min_prof = request.form.get("min_proficiency", "intermediate")
    tip = request.form.get("recommendation_tip", "")

    if not skill_id or not skill_id.isdigit():
        flash("Please select a valid skill.", "danger")
        return redirect(url_for("admin.dashboard"))

    existing = JobRoleSkill.query.filter_by(job_role_id=job_role.id, skill_id=int(skill_id)).first()
    if existing:
        existing.importance_weight = int(weight) if weight.isdigit() else 2
        existing.min_proficiency = min_prof
        existing.recommendation_tip = tip
        flash(f"Updated skill requirement for {job_role.title}.", "info")
    else:
        jrs = JobRoleSkill(
            job_role_id=job_role.id,
            skill_id=int(skill_id),
            importance_weight=int(weight) if weight.isdigit() else 2,
            min_proficiency=min_prof,
            is_required=True,
            recommendation_tip=tip
        )
        db.session.add(jrs)
        flash(f"Added skill requirement to {job_role.title}.", "success")

    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/questions/create", methods=["POST"])
@login_required
@role_required("admin")
@csrf_protect
def create_question():
    assessment_id = request.form.get("assessment_id")
    text = request.form.get("question_text", "").strip()
    a = request.form.get("option_a", "").strip()
    b = request.form.get("option_b", "").strip()
    c = request.form.get("option_c", "").strip()
    d = request.form.get("option_d", "").strip()
    correct = request.form.get("correct_option", "A").strip().upper()
    expl = request.form.get("explanation", "").strip()

    if not assessment_id or not text or not a or not b or not c or not d:
        flash("All question fields are required.", "danger")
        return redirect(url_for("admin.dashboard"))

    q = Question(
        assessment_id=int(assessment_id),
        question_text=text,
        option_a=a,
        option_b=b,
        option_c=c,
        option_d=d,
        correct_option=correct,
        explanation=expl
    )
    db.session.add(q)
    db.session.commit()

    AuditLog.log("QUESTION_CREATED", user_id=current_user.id, details=f"Added question to assessment {assessment_id}")
    flash("Added new practice question successfully.", "success")
    return redirect(url_for("admin.dashboard"))
