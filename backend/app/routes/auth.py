from flask import Blueprint, g, jsonify, request

from app.middleware.auth_middleware import roles_required
from app.schemas.auth_schema import (
    validate_register_payload, validate_login_payload, validate_create_staff_payload,
)
from app.services.auth_service import AuthError, register_user, authenticate_user, issue_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    errors = validate_register_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        user = register_user(
            email=data["email"].strip().lower(),
            password=data["password"],
            full_name=data["full_name"].strip(),
            role="applicant",
        )
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code

    token = issue_token(user)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    errors = validate_login_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        user = authenticate_user(data["email"].strip().lower(), data["password"])
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code

    token = issue_token(user)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.post("/auth/logout")
def logout():
    # Stateless JWT -- logout is handled client-side by discarding the token.
    # (A token-blocklist could be added here if server-side revocation is required.)
    return jsonify({"message": "Logged out."}), 200


@auth_bp.get("/auth/me")
@roles_required("applicant", "loan_officer", "admin")
def me():
    return jsonify({"user": g.current_user.to_dict()}), 200


@auth_bp.post("/auth/create-staff")
@roles_required("admin")
def create_staff():
    """Admin-only: create a loan_officer or admin account."""
    data = request.get_json(silent=True) or {}
    errors = validate_create_staff_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        user = register_user(
            email=data["email"].strip().lower(),
            password=data["password"],
            full_name=data["full_name"].strip(),
            role=data["role"],
        )
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code

    return jsonify({"user": user.to_dict()}), 201
