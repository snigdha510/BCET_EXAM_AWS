from flask import render_template,redirect,Blueprint,url_for
from flask_login import current_user
from flask import request, Blueprint, redirect, render_template, url_for, flash, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from pariksha.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from pariksha.models import User, Student, Teacher
from pariksha.auth.utils import send_reset_email, send_verification_email
from pariksha import bcrypt, db
from urllib.parse import urlparse, urljoin
import requests

main = Blueprint("main",__name__,template_folder="templates",static_folder="static")

# CORS(main, supports_credentials=True) #Registering CORS

@main.route("/")
def welcome():
    if current_user.is_authenticated == False:
        return render_template("welcome.html",title = "Welcome")
    else:
        if current_user.student is not None:
            return redirect(url_for('student.home'))
        else:
            return redirect(url_for('teacher.home'))
        
@main.route("/externalregister", methods=["GET","POST"])
def externalregister():
    # Fetch user details from the external API endpoint
    talent_endpoint = "http://52.66.152.129:2021/api/auth/sendTalentDetailsToTestEnvironemnt"
    talent_response = requests.get(talent_endpoint)
    
    if talent_response.status_code == 200:
        talent_data = talent_response.json()
        name = talent_data.get('name')
        email = talent_data.get('email')
        password = talent_data.get('password')  # Ensure this is hashed appropriately
        acc_type = talent_data.get('acc_type')
        tid=talent_data.get("talentid")
    else:
        return jsonify({"error": "Failed to fetch user details from external API"}), 500
    
    # Post user details to the external register route
    register_data = {
        "name": name,
        "email": email,
        "password": password,
        "acc_type": acc_type,
        "talentid": tid
    }
    external_register_endpoint = "http://52.66.152.129:2028/externalregister"
    external_register_response = requests.post(external_register_endpoint, json=register_data)

    if external_register_response.status_code == 201:
        return jsonify({"message": "User registered successfully"}), 201
    elif external_register_response.status_code == 200:
        return jsonify({"message": "User logged in successfully"}), 200
    else:
        return jsonify({"error": "Failed to register user"}), 500
