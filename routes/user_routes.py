from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from db import mongo
import re


user_bp = Blueprint("users", __name__)

# Validate registration details
def validate_user(name, email, password, phone):

    if not name or not name.strip():
        return "Name Cannot Be Empty"

    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return "Invalid Email Address"

    if len(password) < 8:
        return "Password Must Contain At Least 8 Characters"

    if not re.search(r"[A-Z]", password):
        return "Password needs an uppercase letter"

    if not re.search(r"[a-z]", password):
        return "Password needs a lowercase letter"

    if not re.search(r"[0-9]", password):
        return "Password needs a number"

    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password needs a special character"

    if not re.fullmatch(r"(?:\+91[- ]?)?[6-9]\d{9}", phone):
        return "Invalid Indian phone number"

    return None


# REGISTER
@user_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "")
    email = data.get("email", "").strip()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()

    error = validate_user(name, email, password, phone)

    if error:
        return jsonify({"message": error}), 400

    users = mongo.db.users

    if users.find_one({"email": email.lower()}):
        return jsonify({"message": "Email already registered"}), 409

    hashed_password = generate_password_hash(password)

    user = {
        "name": name.strip(),
        "email": email.lower(),
        "phone": phone,
        "password": hashed_password,
        "role": "customer"
    }

    result = users.insert_one(user)

    token = create_access_token(
        identity=str(result.inserted_id),
        additional_claims={"role": "customer"}
    )

    return jsonify({
        "message": "Registration successful",
        "name": name.strip(),
        "token": token
    }), 201


# LOGIN
@user_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and Password are Required"}), 400

    user = mongo.db.users.find_one({"email": email})
   
    print("LOGIN EMAIL:", email)
    print("USER FOUND:", user is not None)
    
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    if not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    token = create_access_token(
        identity=str(user["_id"]),
        additional_claims={"role": user.get("role", "customer")}
    )

    return jsonify({
        "message": "Login successful",
        "name": user["name"],
        "token": token
    }), 200