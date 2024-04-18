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
from urllib.parse import urlparse, urljoin

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

@main.route("/api/register", methods=["POST"])
def api_register():
    if request.json:
        name = request.json.get('name')
        email = request.json.get('email')
        password = request.json.get('password')
        acc_type = request.json.get('acc_type')
        
        # Check if the user details are present in the talent details endpoint
        talent_endpoint = "http://52.66.152.129:2021/api/auth/sendTalentDetailsToTestEnvironemnt"
        talent_response = requests.get(talent_endpoint)
        if talent_response.status_code == 200:
            talent_data = talent_response.json()
            if email in talent_data:  # Assuming email is the unique identifier
                # Log in the user directly
                user = User.query.filter_by(email=email).first()
                if user:
                    login_user(user, remember=False)
                    return jsonify({"message": "User logged in successfully", "user_id": user.id}), 200

        # If user details are not present in talent details, proceed with registration
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

@main.route("/login", methods=["POST", "GET"])
def api_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check if the user details are present in the talent details endpoint
        talent_endpoint = "http://52.66.152.129:2021/api/auth/sendTalentDetailsToTestEnvironemnt"
        talent_response = requests.get(talent_endpoint)
        
        if talent_response.status_code == 200:
            talent_data = talent_response.json()
            
            if email == talent_data.get("email"):  # Compare email directly
                user = User.query.filter_by(email=email).first()
                
                if user and bcrypt.check_password_hash(user.password, password):
                    # Get quiz URL details
                    customer_id = talent_data.get("customerId")
                    job_id = talent_data.get("jobId")
                    quiz_access_url = "http://your-quiz-url"  # Replace with actual quiz URL
                    
                    # Update quiz URL via API endpoint
                    update_endpoint = "http://52.66.152.129:2021/api/auth/updateBcetjdtdFromChatbotUniqueLink"
                    payload = {"customerId": customer_id, "jobId": job_id, "uniqueLink": quiz_access_url}
                    update_response = requests.put(update_endpoint, json=payload)
                    
                    if update_response.status_code == 200:
                        # Redirect user to the quiz URL
                        return redirect(quiz_access_url)

                    flash("Failed to update quiz URL. Please try again later.", "danger")
                else:
                    flash("Incorrect email or password. Please try again.", "danger")
            else:
                flash("User not found in talent details. Please register or contact support.", "danger")
        else:
            flash("Failed to fetch talent details. Please try again later.", "danger")

    return render_template("login.html", form=form, title="Login")