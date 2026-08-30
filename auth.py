from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth = Blueprint("auth", __name__)


# ─── Page Routes ────────────────────────────────────────────────────────────

@auth.route("/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("login.html")


@auth.route("/register", methods=["GET"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("register.html")


# ─── API Routes ─────────────────────────────────────────────────────────────

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "username, email, and password are required"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
    )
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({"message": "Account created successfully", "username": user.username}), 201


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid username or password"}), 401

    login_user(user)
    return jsonify({"message": "Logged in successfully", "username": user.username}), 200


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login_page"))


@auth.route("/api/me")
def me():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "username": current_user.username})
    return jsonify({"logged_in": False})
