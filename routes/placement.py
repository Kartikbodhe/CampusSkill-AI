import io
import csv
from collections import Counter
from flask import Blueprint, render_template, request, make_response, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.user import User, StudentProfile
from models.skills import StudentSkill
from models.jobs import JobRole
from models.assessments import AssessmentAttempt
from models.audit import AuditLog
from services.readiness import calculate_placement_readiness
from services.skill_gap import analyze_skill_gap
from utils.security import role_required

placement_bp = Blueprint("placement", __name__, url_prefix="/placement")


@placement_bp.route("/dashboard", methods=["GET"])
@login_required
@role_required("placement_officer", "admin")
def dashboard():
    # Fetch all students
    all_students = StudentProfile.query.all()
    total_students = len(all_students)

    # Search and Filter Parameters
    q = request.args.get("q", "").strip().lower()
    selected_branch = request.args.get("branch", "").strip()
    selected_year = request.args.get("year", "").strip()
    min_score = request.args.get("min_score", "").strip()

    # Pre-calculate scores and distributions
    student_records = []
    branch_counts = Counter()
    year_counts = Counter()
    readiness_bands = {"Ready": 0, "Moderate": 0, "NeedsPrep": 0}
    scores_sum = 0
    missing_skills_counter = Counter()

    for sp in all_students:
        branch_counts[sp.branch] += 1
        year_counts[sp.current_year] += 1
        
        # Calculate readiness score
        r_data = calculate_placement_readiness(sp)
        score = r_data["overall_score"]
        scores_sum += score

        if score >= 75.0:
            readiness_bands["Ready"] += 1
        elif score >= 50.0:
            readiness_bands["Moderate"] += 1
        else:
            readiness_bands["NeedsPrep"] += 1

        # Calculate gaps if role is selected to aggregate common missing skills
        if sp.target_job_role:
            gap = analyze_skill_gap(sp, sp.target_job_role)
            if gap:
                for ms in gap["missing_skills"]:
                    missing_skills_counter[ms["skill_name"]] += 1

        # Apply search and filter
        matches_query = not q or (q in sp.full_name.lower() or (sp.user and q in sp.user.email.lower()))
        matches_branch = not selected_branch or (sp.branch == selected_branch)
        matches_year = not selected_year or (sp.current_year == selected_year)
        matches_min_score = True
        if min_score.isdigit():
            matches_min_score = (score >= float(min_score))

        if matches_query and matches_branch and matches_year and matches_min_score:
            student_records.append({
                "profile": sp,
                "readiness": r_data,
                "score": score,
                "skills_count": len(sp.skills),
                "target_role": sp.target_job_role.title if sp.target_job_role else "Unassigned",
            })

    avg_score = round(scores_sum / total_students, 1) if total_students > 0 else 0.0
    top_missing_skills = missing_skills_counter.most_common(6)

    # Sort filtered student records by readiness score descending
    student_records.sort(key=lambda x: x["score"], reverse=True)

    available_branches = sorted(list(branch_counts.keys()))
    available_years = sorted(list(year_counts.keys()))

    return render_template(
        "placement/dashboard.html",
        total_students=total_students,
        avg_score=avg_score,
        branch_counts=dict(branch_counts),
        year_counts=dict(year_counts),
        readiness_bands=readiness_bands,
        top_missing_skills=top_missing_skills,
        student_records=student_records,
        available_branches=available_branches,
        available_years=available_years,
        filter_q=q,
        filter_branch=selected_branch,
        filter_year=selected_year,
        filter_min_score=min_score
    )


@placement_bp.route("/student/<int:student_id>", methods=["GET"])
@login_required
@role_required("placement_officer", "admin")
def view_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    readiness = calculate_placement_readiness(student)
    gap_data = analyze_skill_gap(student, student.target_job_role) if student.target_job_role else None
    attempts = AssessmentAttempt.query.filter_by(student_profile_id=student.id).order_by(AssessmentAttempt.attempted_at.desc()).all()

    return render_template(
        "placement/student_detail.html",
        student=student,
        readiness=readiness,
        gap_data=gap_data,
        attempts=attempts
    )


@placement_bp.route("/export-csv", methods=["GET"])
@login_required
@role_required("placement_officer", "admin")
def export_csv():
    # Filter parameters can also apply to export
    selected_branch = request.args.get("branch", "").strip()
    selected_year = request.args.get("year", "").strip()

    students = StudentProfile.query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student ID", "Full Name", "Email", "College", "Branch", "Current Year",
        "Graduation Year", "Target Role", "Overall Readiness Score", "Readiness Band",
        "Recorded Skills Count", "Verified Assessments Count"
    ])

    for sp in students:
        if selected_branch and sp.branch != selected_branch:
            continue
        if selected_year and sp.current_year != selected_year:
            continue

        r = calculate_placement_readiness(sp)
        verified_count = sum(1 for att in sp.assessment_attempts if att.passed)

        writer.writerow([
            sp.id,
            sp.full_name,
            sp.user.email if sp.user else "N/A",
            sp.college_name,
            sp.branch,
            sp.current_year,
            sp.graduation_year,
            sp.target_job_role.title if sp.target_job_role else "Not Selected",
            f"{r['overall_score']}%",
            r["band"],
            len(sp.skills),
            verified_count
        ])

    AuditLog.log("EXPORT_CSV", user_id=current_user.id, details="Exported student placement readiness report to CSV")

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=campusskill_student_readiness_report.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response
