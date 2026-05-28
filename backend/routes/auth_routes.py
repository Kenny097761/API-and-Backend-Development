from flask import Blueprint, request, jsonify, session
from backend.models.db_crud import login_user, get_user_details

from backend.models.access_logs_service import (
    create_login_log,
    update_logout_log
)

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["POST"])
def login_route():

    if request.is_json:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

    user = login_user(email, password)

    if user is None:
        return jsonify({"success": False, "status": "error", "message": "Invalid email or password"}), 401
    
    # Create Access Log
    log_id = create_login_log(user["user_id"])

    session.clear()
    session["user_id"] = user["user_id"]
    session["role"] = user["role"]

    # Store Access Log ID
    session["log_id"] = log_id

    return jsonify({
        "success": True,
        "status": "success",
        "message": "Login successful",
        "user": user
    })


@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Not logged in"
        }), 401

    user = get_user_details(user_id)
    if user is None:
        return jsonify({
            "status": "error",
            "message": "Not logged in"
        }), 401

    return jsonify({
        "status": "success",
        "user": user
    })


@auth_bp.route("/logout", methods=["POST"])
def logout_route():

    # Get Access Log session
    log_id = session.get("log_id")

    # Update logout time
    if log_id:
        try:
            update_logout_log(log_id)
        except Exception:
            pass

    session.pop("user_id", None)
    session.pop("role", None)

    # Remove log session
    session.pop("log_id", None)

    return jsonify({
        "success": True, 
        "status": "success", 
        "message": 
        "Logged out"
    })

