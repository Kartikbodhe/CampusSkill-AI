from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.jobs import JobRole
from services.skill_gap import analyze_skill_gap
from utils.security import role_required, csrf_protect

analyzer_bp = Blueprint("analyzer", __name__, url_prefix="/analyzer")


@analyzer_bp.route("/", methods=["GET"])
@login_required
@role_required("student")
def view_analyzer():
    profile = current_user.student_profile
    all_roles = JobRole.query.order_by(JobRole.title).all()

    # Determine which role to analyze: query param 'role_id' > profile.target_job_role_id > first available
    role_id = request.args.get("role_id")
    selected_role = None

    if role_id and role_id.isdigit():
        selected_role = JobRole.query.get(int(role_id))
    
    if not selected_role and profile.target_job_role:
        selected_role = profile.target_job_role
    elif not selected_role and all_roles:
        selected_role = all_roles[0]

    gap_data = analyze_skill_gap(profile, selected_role) if selected_role else None

    return render_template(
        "student/analyzer.html",
        profile=profile,
        all_roles=all_roles,
        selected_role=selected_role,
        gap_data=gap_data
    )


@analyzer_bp.route("/set-target/<int:role_id>", methods=["POST"])
@login_required
@role_required("student")
@csrf_protect
def set_target_role(role_id):
    profile = current_user.student_profile
    role = JobRole.query.get_or_404(role_id)

    profile.target_job_role_id = role.id
    db.session.commit()

    flash(f"Set target job role to {role.title}!", "success")
    return redirect(url_for("analyzer.view_analyzer", role_id=role.id))
