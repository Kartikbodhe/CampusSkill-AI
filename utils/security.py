import os
import secrets
from functools import wraps
from flask import session, request, abort, current_app, flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename


def get_or_create_csrf_token():
    """Ensure a CSRF token exists in the user's session and return it."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def validate_csrf():
    """Verify CSRF token from form or headers."""
    # Allow bypass in testing if explicitly disabled
    if current_app.config.get("TESTING") and not current_app.config.get("WTF_CSRF_ENABLED", False):
        return True
    
    token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
    session_token = session.get("_csrf_token")
    
    if not token or not session_token or not secrets.compare_digest(token, session_token):
        abort(400, description="Invalid or missing CSRF token.")
    return True


def csrf_protect(f):
    """Decorator to enforce CSRF validation on mutating HTTP methods."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            validate_csrf()
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """Decorator to restrict view access to specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.path))
            if current_user.role not in allowed_roles:
                abort(403, description="You do not have permission to access this resource.")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "docx", "doc"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def save_secure_resume(file_storage, user_id):
    """Save an uploaded resume with a secure, randomized filename."""
    if not file_storage or file_storage.filename == "":
        return None
        
    orig_name = secure_filename(file_storage.filename)
    if not allowed_file(orig_name):
        return False
        
    ext = orig_name.rsplit(".", 1)[1].lower()
    random_hex = secrets.token_hex(8)
    safe_filename = f"resume_{user_id}_{random_hex}.{ext}"
    
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    destination = os.path.join(upload_folder, safe_filename)
    file_storage.save(destination)
    return safe_filename
