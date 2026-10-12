from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User, StudentProfile
from models.jobs import JobRole
from models.audit import AuditLog
from utils.security import csrf_protect

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
@csrf_protect
def register():
    if current_user.is_authenticated:
        return redirect_to_role_home(current_user)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        branch = request.form.get("branch", "Computer Science").strip()
        current_year = request.form.get("current_year", "3rd Year").strip()
        target_role_id = request.form.get("target_job_role_id")

        # Validation
        if not full_name or not email or not password:
            flash("All mandatory fields are required.", "danger")
            return render_template("auth/register.html", job_roles=JobRole.query.all())

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html", job_roles=JobRole.query.all())

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("auth/register.html", job_roles=JobRole.query.all())

        # Email format check
        if "@" not in email or "." not in email:
            flash("Please provide a valid email address.", "danger")
            return render_template("auth/register.html", job_roles=JobRole.query.all())

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        # Create user (Always forced to role='student' for public registration)
        new_user = User(email=email, role="student")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Create student profile
        profile = StudentProfile(
            user_id=new_user.id,
            full_name=full_name,
            branch=branch,
            current_year=current_year,
            target_job_role_id=int(target_role_id) if target_role_id and target_role_id.isdigit() else None
        )
        db.session.add(profile)
        db.session.commit()

        AuditLog.log("STUDENT_REGISTERED", user_id=new_user.id, ip_address=request.remote_addr, details=f"Registered {email}")
        flash("Registration successful! You may now sign in.", "success")
        return redirect(url_for("auth.login"))

    job_roles = JobRole.query.order_by(JobRole.title).all()
    return render_template("auth/register.html", job_roles=job_roles)


@auth_bp.route("/login", methods=["GET", "POST"])
@csrf_protect
def login():
    if current_user.is_authenticated:
        return redirect_to_role_home(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("This account is currently deactivated. Please contact the administrator.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        AuditLog.log("USER_LOGIN", user_id=user.id, ip_address=request.remote_addr, details=f"Logged in via web form")

        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)

        return redirect_to_role_home(user)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    user_id = current_user.id
    logout_user()
    AuditLog.log("USER_LOGOUT", user_id=user_id, ip_address=request.remote_addr)
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))


def redirect_to_role_home(user):
    """Route user to their designated dashboard based on role."""
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))
    elif user.is_placement_officer:
        return redirect(url_for("placement.dashboard"))
    else:
        return redirect(url_for("student.dashboard"))
