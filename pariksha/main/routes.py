from flask import render_template,redirect,Blueprint,url_for
from flask_login import current_user
from flask import request, Blueprint, redirect, render_template, url_for, flash, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from pariksha.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from pariksha.models import User, Student, Teacher
from pariksha.auth.utils import send_reset_email, send_verification_email
from pariksha import bcrypt, db
from urllib.parse import urlparse, urljoin
from flask_cors import cross_origin, CORS
import requests

main = Blueprint("main",__name__,template_folder="templates",static_folder="static")

CORS(main, supports_credentials=True) #Registering CORS

@main.route("/")
def welcome():
    if current_user.is_authenticated == False:
        return render_template("welcome.html",title = "Welcome")
    else:
        if current_user.student is not None:
            return redirect(url_for('student.home'))
        else:
            return redirect(url_for('teacher.home'))
        
@main.route("/externalregister", methods=["POST"])
def externalregister():
    if request.json:
        # Fetch user details from the external API endpoint
        talent_endpoint = "http://52.66.152.129:2021/api/auth/sendTalentDetailsToTestEnvironemnt"
        talent_response = requests.get(talent_endpoint)
        
        if talent_response.status_code == 200:
            talent_data = talent_response.json()
            name = talent_data.get('name')
            email = talent_data.get('email')
            password = talent_data.get('password')  
            acc_type = talent_data.get('acc_type')
        else:
            return jsonify({"error": "Failed to fetch user details from external API"}), 500
        
        # Check if the user with the provided email is already registered
        user = User.query.filter_by(email=email).first()
        if user:
            # If user is registered, log them in
            login_user(user, remember=False)
            return jsonify({"message": "User logged in successfully", "user_id": user.id}), 200
        
        # If user is not registered, proceed with registration
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password=hashed_password)
        
        if acc_type == "Student":
            student = Student(user=user)
            db.session.add(student)
        elif acc_type == "Teacher":
            teacher = Teacher(user=user)
            db.session.add(teacher)
        else:
            return jsonify({"error": "Invalid account type"}), 400

        db.session.add(user)
        db.session.commit()
        
        return jsonify({"message": "User registered successfully", "user_id": user.id}), 201
    else:
        return jsonify({"error": "Invalid request format"}), 400