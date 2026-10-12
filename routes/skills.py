from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.skills import Skill, StudentSkill
from utils.security import role_required, csrf_protect

skills_bp = Blueprint("skills", __name__, url_prefix="/skills")


@skills_bp.route("/", methods=["GET"])
@login_required
@role_required("student")
def manage_skills():
    profile = current_user.student_profile
    student_skills = StudentSkill.query.filter_by(student_profile_id=profile.id).all()
    user_skill_ids = {ss.skill_id for ss in student_skills}

    all_catalog_skills = Skill.query.order_by(Skill.category, Skill.name).all()
    available_catalog = [s for s in all_catalog_skills if s.id not in user_skill_ids]

    return render_template(
        "student/skills.html",
        student_skills=student_skills,
        available_catalog=available_catalog,
        all_catalog_skills=all_catalog_skills
    )


@skills_bp.route("/add", methods=["POST"])
@login_required
@role_required("student")
@csrf_protect
def add_skill():
    profile = current_user.student_profile
    skill_id = request.form.get("skill_id")
    proficiency = request.form.get("proficiency_level", "beginner").lower()

    if not skill_id or not skill_id.isdigit():
        flash("Invalid skill selected.", "danger")
        return redirect(url_for("skills.manage_skills"))

    skill = Skill.query.get(int(skill_id))
    if not skill:
        flash("Skill not found in catalog.", "danger")
        return redirect(url_for("skills.manage_skills"))

    if proficiency not in ["beginner", "intermediate", "advanced"]:
        proficiency = "beginner"

    existing = StudentSkill.query.filter_by(
        student_profile_id=profile.id,
        skill_id=skill.id
    ).first()

    if existing:
        existing.proficiency_level = proficiency
        flash(f"Updated proficiency for {skill.name} to {proficiency.capitalize()}.", "info")
    else:
        new_ss = StudentSkill(
            student_profile_id=profile.id,
            skill_id=skill.id,
            proficiency_level=proficiency,
            verified=False
        )
        db.session.add(new_ss)
        flash(f"Added {skill.name} ({proficiency.capitalize()}) to your profile.", "success")

    db.session.commit()
    return redirect(url_for("skills.manage_skills"))


@skills_bp.route("/update/<int:skill_entry_id>", methods=["POST"])
@login_required
@role_required("student")
@csrf_protect
def update_skill(skill_entry_id):
    profile = current_user.student_profile
    student_skill = StudentSkill.query.filter_by(
        id=skill_entry_id,
        student_profile_id=profile.id
    ).first_or_404()

    new_level = request.form.get("proficiency_level", "").lower()
    if new_level in ["beginner", "intermediate", "advanced"]:
        student_skill.proficiency_level = new_level
        db.session.commit()
        flash(f"Proficiency for {student_skill.skill.name} updated to {new_level.capitalize()}.", "success")
    else:
        flash("Invalid proficiency level provided.", "danger")

    return redirect(url_for("skills.manage_skills"))


@skills_bp.route("/delete/<int:skill_entry_id>", methods=["POST"])
@login_required
@role_required("student")
@csrf_protect
def delete_skill(skill_entry_id):
    profile = current_user.student_profile
    student_skill = StudentSkill.query.filter_by(
        id=skill_entry_id,
        student_profile_id=profile.id
    ).first_or_404()

    skill_name = student_skill.skill.name
    db.session.delete(student_skill)
    db.session.commit()

    flash(f"Removed {skill_name} from your profile.", "info")
    return redirect(url_for("skills.manage_skills"))
