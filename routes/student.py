import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from extensions import db
from models.jobs import JobRole
from models.assessments import AssessmentAttempt
from models.roadmap import Roadmap
from services.skill_gap import analyze_skill_gap
from services.readiness import calculate_placement_readiness
from services.role_matcher import recommend_matching_roles
from utils.security import role_required, csrf_protect, save_secure_resume

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    profile = current_user.student_profile
    if not profile:
        flash("Please complete your student profile.", "info")
        return redirect(url_for("student.profile"))

    # Calculate explainable placement readiness
    readiness = calculate_placement_readiness(profile)

    # Perform gap analysis if target role is selected
    gap_analysis = None
    if profile.target_job_role:
        gap_analysis = analyze_skill_gap(profile, profile.target_job_role)

    # Fetch active learning roadmap
    active_roadmap = Roadmap.query.filter_by(
        student_profile_id=profile.id,
        target_job_role_id=profile.target_job_role_id
    ).first() if profile.target_job_role_id else None

    # Fetch recent assessment attempts
    recent_attempts = AssessmentAttempt.query.filter_by(
        student_profile_id=profile.id
    ).order_by(AssessmentAttempt.attempted_at.desc()).limit(5).all()

    # Get recommended job roles matching student's skillset
    recommended_roles = recommend_matching_roles(profile, limit=4)

    return render_template(
        "student/dashboard.html",
        profile=profile,
        readiness=readiness,
        gap_analysis=gap_analysis,
        active_roadmap=active_roadmap,
        recent_attempts=recent_attempts,
        recommended_roles=recommended_roles
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("student")
@csrf_protect
def profile():
    profile = current_user.student_profile

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        college_name = request.form.get("college_name", "").strip()
        branch = request.form.get("branch", "Computer Science").strip()
        current_year = request.form.get("current_year", "3rd Year").strip()
        graduation_year = request.form.get("graduation_year", "2026").strip()
        career_objective = request.form.get("career_objective", "").strip()
        target_role_id = request.form.get("target_job_role_id")
        github_url = request.form.get("github_url", "").strip()
        linkedin_url = request.form.get("linkedin_url", "").strip()

        if not full_name:
            flash("Full name is required.", "danger")
            return redirect(url_for("student.profile"))

        profile.full_name = full_name
        profile.college_name = college_name
        profile.branch = branch
        profile.current_year = current_year
        if graduation_year.isdigit():
            profile.graduation_year = int(graduation_year)
        profile.career_objective = career_objective
        profile.target_job_role_id = int(target_role_id) if target_role_id and target_role_id.isdigit() else None
        profile.github_url = github_url
        profile.linkedin_url = linkedin_url

        # Handle optional resume upload
        if "resume_file" in request.files:
            file = request.files["resume_file"]
            if file and file.filename != "":
                saved_filename = save_secure_resume(file, current_user.id)
                if saved_filename is False:
                    flash("Invalid file type. Only PDF and DOCX documents are permitted.", "danger")
                    return redirect(url_for("student.profile"))
                elif saved_filename:
                    # Clean up previous resume if present
                    if profile.resume_filename:
                        old_path = os.path.join(current_app.config.get("UPLOAD_FOLDER", "uploads"), profile.resume_filename)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except OSError:
                                pass
                    profile.resume_filename = saved_filename
                    flash("Resume uploaded successfully.", "success")

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("student.profile"))

    job_roles = JobRole.query.order_by(JobRole.title).all()
    return render_template("student/profile.html", profile=profile, job_roles=job_roles)


@student_bp.route("/resume/download")
@login_required
def download_resume():
    """Secure endpoint for downloading the student resume."""
    profile = current_user.student_profile
    if not profile or not profile.resume_filename:
        abort(404, description="No resume uploaded.")

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    return send_from_directory(
        upload_folder,
        profile.resume_filename,
        as_attachment=True,
        download_name=f"{profile.full_name.replace(' ', '_')}_Resume.pdf"
    )
