from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import hashlib
from datetime import timedelta

from app import extensions
from app.models import User
from app.db import create_password_reset_token, is_password_reset_token_valid, mark_password_reset_token_used

auth_bp = Blueprint("auth", __name__)


def _get_serializer():
    from flask import current_app

    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="vidyastra-reset")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        if extensions.mongo_db is None:
            flash("Authentication is unavailable until MongoDB is connected.", "error")
            return render_template("auth/signup.html")

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template("auth/signup.html")

        if extensions.mongo_db.users.find_one({"email": email}):
            flash("An account with this email already exists.", "error")
            return render_template("auth/signup.html")

        extensions.mongo_db.users.insert_one(
            {
                "name": name,
                "email": email,
                "password_hash": generate_password_hash(password),
                "created_at": datetime.utcnow(),
            }
        )
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        if extensions.mongo_db is None:
            flash("Authentication is unavailable until MongoDB is connected.", "error")
            return render_template("auth/login.html")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user_doc = extensions.mongo_db.users.find_one({"email": email})
        if not user_doc or not check_password_hash(user_doc.get("password_hash", ""), password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        login_user(User.from_document(user_doc), remember=True)
        return redirect(url_for("dashboard.home"))

    return render_template("auth/login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Email is required.", "error")
            return render_template("auth/forgot_password.html")

        if extensions.mongo_db is None:
            flash("Password reset is unavailable until MongoDB is connected.", "error")
            return render_template("auth/forgot_password.html")

        user_doc = extensions.mongo_db.users.find_one({"email": email})
        # Don't reveal if account exists.
        token = _get_serializer().dumps({"email": email})
        token_hash = _hash_token(token)
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        try:
            create_password_reset_token(email=email, token_hash=token_hash, expires_at=expires_at)
        except Exception:
            pass

        reset_link = url_for("auth.reset_password", token=token, _external=True)
        # Email delivery is mocked: show link via flash in dev.
        if user_doc:
            flash(f"Reset link (dev): {reset_link}", "success")
        else:
            flash("If that email exists, we’ve sent a reset link.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    email = None
    try:
        data = _get_serializer().loads(token, max_age=30 * 60)
        email = (data.get("email") or "").strip().lower()
    except SignatureExpired:
        flash("Reset link expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("Invalid reset link.", "error")
        return redirect(url_for("auth.forgot_password"))

    token_hash = _hash_token(token)
    if not email or not is_password_reset_token_valid(email=email, token_hash=token_hash):
        flash("Reset link is invalid or already used.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth/reset_password.html", token=token)
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("auth/reset_password.html", token=token)

        if extensions.mongo_db is None:
            flash("Password reset is unavailable until MongoDB is connected.", "error")
            return render_template("auth/reset_password.html", token=token)

        extensions.mongo_db.users.update_one(
            {"email": email},
            {"$set": {"password_hash": generate_password_hash(password), "updated_at": datetime.utcnow()}},
        )
        mark_password_reset_token_used(email=email, token_hash=token_hash)
        flash("Password updated. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("dashboard.landing"))


@auth_bp.route("/auth/login")
def login_legacy_redirect():
    return redirect(url_for("auth.login"))


@auth_bp.route("/auth/signup")
def signup_legacy_redirect():
    return redirect(url_for("auth.signup"))


@auth_bp.route("/auth/logout")
def logout_legacy_redirect():
    return redirect(url_for("auth.logout"))
