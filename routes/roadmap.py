from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.jobs import JobRole
from models.roadmap import Roadmap, RoadmapTask
from services.roadmap_generator import generate_or_update_roadmap
from utils.security import role_required, csrf_protect

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/roadmap")


@roadmap_bp.route("/", methods=["GET"])
@login_required
@role_required("student")
def view_roadmap():
    profile = current_user.student_profile
    if not profile.target_job_role:
        flash("Please select a target job role before accessing your learning roadmap.", "warning")
        return redirect(url_for("analyzer.view_analyzer"))

    roadmap = Roadmap.query.filter_by(
        student_profile_id=profile.id,
        target_job_role_id=profile.target_job_role_id
    ).first()

    # Automatically generate if not yet generated
    if not roadmap:
        roadmap = generate_or_update_roadmap(profile, profile.target_job_role)

    # Group tasks by phase
    phases = {1: [], 2: [], 3: [], 4: []}
    if roadmap:
        for task in roadmap.tasks:
            phases.setdefault(task.phase, []).append(task)

    return render_template(
        "student/roadmap.html",
        profile=profile,
        roadmap=roadmap,
        phases=phases,
        job_role=profile.target_job_role
    )


@roadmap_bp.route("/generate", methods=["POST"])
@login_required
@role_required("student")
@csrf_protect
def generate_roadmap():
    profile = current_user.student_profile
    if not profile.target_job_role:
        flash("Please select a target job role first.", "warning")
        return redirect(url_for("analyzer.view_analyzer"))

    roadmap = generate_or_update_roadmap(profile, profile.target_job_role)
    flash(f"Personalized roadmap refreshed for {profile.target_job_role.title}!", "success")
    return redirect(url_for("roadmap.view_roadmap"))


@roadmap_bp.route("/task/<int:task_id>/toggle", methods=["POST"])
@login_required
@role_required("student")
@csrf_protect
def toggle_task(task_id):
    profile = current_user.student_profile
    task = RoadmapTask.query.get_or_404(task_id)

    # Ensure ownership via roadmap relationship
    if task.roadmap.student_profile_id != profile.id:
        flash("Unauthorized task modification.", "danger")
        return redirect(url_for("roadmap.view_roadmap"))

    task.is_completed = not task.is_completed
    task.completed_at = datetime.now(timezone.utc) if task.is_completed else None
    
    completion_pct = task.roadmap.recalculate_completion()
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "is_completed": task.is_completed,
            "completion_percentage": completion_pct
        })

    flash("Task progress updated.", "info")
    return redirect(url_for("roadmap.view_roadmap"))
