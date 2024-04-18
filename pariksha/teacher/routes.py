from flask import render_template, Blueprint, flash, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user, logout_user
from pariksha.models import Quiz, Quiz_Questions, Student, User
from pariksha import db
import csv
import json
import requests
from flask import flash, redirect, request, url_for
from datetime import datetime, timedelta
from flask import jsonify
import logging

teacher = Blueprint('teacher', __name__, url_prefix="/teacher", template_folder='templates', static_folder="static")


@teacher.route('/home')
def home():
    if current_user.teacher is None:
        flash("Permission denied to access the page", 'danger')
        return redirect(url_for('student.home'))
    return render_template('teacher_home.html', title='Home')


@teacher.route("/create_new_quiz")
@login_required
def create_new_quiz():
    if current_user.teacher is None:
        flash("Permission denied to access the page", 'danger')
        return redirect(url_for('student.home'))
    return render_template('create_quiz.html', title='Create Quiz')


@teacher.route("/create_new_quiz", methods=['POST'])
@login_required
def create_new_quiz_post():

    current_teacher = current_user.teacher

    try:
        api_endpoint = "http://52.66.152.129:2021/api/auth/getBcetQuestion"
        response = requests.get(api_endpoint)
        response.raise_for_status()
        data = response.json()
        
        # Extract the quiz data key
        quiz_data_key = list(data.keys())[0]
        # Extract the customer ID and job ID from the key
        customer_id, job_id = map(int, quiz_data_key.split('_'))
        
        quiz_data = json.loads(data[quiz_data_key])
        
        quiz = Quiz(
            title=quiz_data['quiz_title'],
            start_time=datetime.fromtimestamp(quiz_data['start_time'] / 1000),
            end_time=datetime.fromtimestamp(quiz_data['end_time'] / 1000),
            teacher_id=current_teacher.id,
            active=True
            )
        db.session.add(quiz)
        total_marks = 0
        
        for question_data in quiz_data['questions']:
            question = Quiz_Questions(
                question_desc=question_data['question_desc'],
                option_1=question_data['option_1'],
                option_2=question_data['option_2'],
                option_3=question_data['option_3'],
                option_4=question_data['option_4'],
                marks=question_data['marks'],
                quiz=quiz
                )
            total_marks += question.marks
            db.session.add(question)
            
            quiz.marks = total_marks
            
            db.session.commit()
            
            quiz_access_url = url_for('student.quiz', quiz_id=quiz.id, _external=True)
            
            # Prepare data for sending to the API endpoint
            payload = {
                "customerId": customer_id,
                "jobId": job_id,
                "uniqueLink": quiz_access_url
                }
            
            logging.info("Sending payload to API endpoint:")
            logging.info(payload)
            
            # Send data to the API endpoint using PUT method
            update_endpoint = "http://52.66.152.129:2021/api/auth/updateBcetjdtdFromChatbotUniqueLink"
            update_response = requests.put(update_endpoint, json=payload)
            update_response.raise_for_status()
            
            # Clear the HashMap data from the API endpoint
            clear_endpoint = "http://52.66.152.129:2021/api/auth/clearBcsetQuestionById/{customer_id}_{job_id}"
            clear_response = requests.post(clear_endpoint)
            clear_response.raise_for_status()
            
            # Success message for sending data to the API
            api_success_message = "Data sent to the API successfully and HashMap cleared!"
            
            return jsonify({
                'status': 'success',
                'message': 'Quiz created and activated successfully!',
                'quizUrl': quiz_access_url,
                'apiMessage': api_success_message
                }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create quiz: ' + str(e)
            }), 500
    
@teacher.route('/create_new_quiz_api/<int:id>', methods=['POST'])
def create_new_quiz_post_api(id):

    current_teacher = User.query.filter_by(id=id).first()

    if current_teacher is None:
        return jsonify({
            'message' : 'enter correct id'
        }), 400
        

    try:
        api_endpoint = "http://52.66.152.129:2021/api/auth/getBcetQuestion"
        response = requests.get(api_endpoint)
        response.raise_for_status()
        data = response.json()
        
        # Extract the quiz data key
        quiz_data_key = list(data.keys())[0]
        # Extract the customer ID and job ID from the key
        customer_id, job_id = map(int, quiz_data_key.split('_'))
        
        quiz_data = json.loads(data[quiz_data_key])
        
        quiz = Quiz(
            title=quiz_data['quiz_title'],
            start_time=datetime.fromtimestamp(quiz_data['start_time'] / 1000),
            end_time=datetime.fromtimestamp(quiz_data['end_time'] / 1000),
            teacher_id=current_teacher.id,
            active=True
            )
        db.session.add(quiz)
        total_marks = 0
        
        for question_data in quiz_data['questions']:
            question = Quiz_Questions(
                question_desc=question_data['question_desc'],
                option_1=question_data['option_1'],
                option_2=question_data['option_2'],
                option_3=question_data['option_3'],
                option_4=question_data['option_4'],
                marks=question_data['marks'],
                quiz=quiz
                )
            total_marks += question.marks
            db.session.add(question)
            
            quiz.marks = total_marks
            
            db.session.commit()
            
            quiz_access_url = url_for('student.quiz', quiz_id=quiz.id, _external=True)
            
            # Prepare data for sending to the API endpoint
            payload = {
                "customerId": customer_id,
                "jobId": job_id,
                "uniqueLink": quiz_access_url
                }
            
            logging.info("Sending payload to API endpoint:")
            logging.info(payload)
            
            # Send data to the API endpoint using PUT method
            update_endpoint = "http://52.66.152.129:2021/api/auth/updateBcetjdtdFromChatbotUniqueLink"
            update_response = requests.put(update_endpoint, json=payload)
            update_response.raise_for_status()
            
            # Clear the HashMap data from the API endpoint
            clear_endpoint = "http://52.66.152.129:2021/api/auth/clearBcsetQuestionById/{customer_id}_{job_id}"
            clear_response = requests.post(clear_endpoint)
            clear_response.raise_for_status()
            
            # Success message for sending data to the API
            api_success_message = "Data sent to the API successfully and HashMap cleared!"
            
            return jsonify({
                'status': 'success',
                'message': 'Quiz created and activated successfully!',
                'quizUrl': quiz_access_url,
                'apiMessage': api_success_message
                }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create quiz: ' + str(e)
            }), 500

    # if request.json and request.json.get('fetchQuizBtn'):
    #     return jsonify({
    #         'status': 'error',
    #         'message': 'No action triggered.'
    #     }), 400

    # current_teacher = current_user.teacher

    # try:
    #     api_endpoint = "http://52.66.152.129:2021/api/auth/getBcetQuestion"
    #     response = requests.get(api_endpoint)
    #     response.raise_for_status()
    #     data = response.json()
        
    #     # Extract the quiz data using the key '6_16'
    #     quiz_data = json.loads(data['6_16'])
        
    #     quiz = Quiz(
    #         title=quiz_data['quiz_title'],
    #         start_time=datetime.fromtimestamp(quiz_data['start_time'] / 1000),
    #         end_time=datetime.fromtimestamp(quiz_data['end_time'] / 1000),
    #         teacher_id=current_teacher.id,
    #         active=True
    #         )
    #     db.session.add(quiz)
    #     total_marks = 0
        
    #     for question_data in quiz_data['questions']:
    #         question = Quiz_Questions(
    #             question_desc=question_data['question_desc'],
    #             option_1=question_data['option_1'],
    #             option_2=question_data['option_2'],
    #             option_3=question_data['option_3'],
    #             option_4=question_data['option_4'],
    #             marks=question_data['marks'],
    #             quiz=quiz
    #             )
    #         total_marks += question.marks
    #         db.session.add(question)
            
    #         quiz.marks = total_marks
    #         db.session.commit()
            
    #         quiz_access_url = url_for('student.quiz', quiz_id=quiz.id, _external=True)
    #         return jsonify({
    #             'status': 'success',
    #             'message': 'Quiz created and activated successfully!',
    #             'quizUrl': quiz_access_url
    #         }), 200
    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({
    #         'status': 'error',
    #         'message': 'Failed to create quiz: ' + str(e)
    #         }), 500

@teacher.route('/activate_quiz_list')
@login_required
def activate_quiz_list():
    if current_user.teacher is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('student.home'))
    # Fetch all active quizzes
    quiz_list = Quiz.query.filter(Quiz.start_time <= datetime.now(), Quiz.end_time >= datetime.now()).all()
    # Check if quizzes exist
    quiz_exists = bool(quiz_list)
    return render_template('quiz_list_activate.html', title='Activate Quiz', quiz_list=quiz_list, quiz_exists=quiz_exists)


# @teacher.route('/activate_quiz/<int:quiz_id>')
# @login_required
# def activate_quiz(quiz_id):
#     if current_user.teacher is None:
#         flash('Access Denide', 'danger')
#         return redirect(url_for('student.home'))
#     teacher = current_user.teacher
#     quiz = Quiz.query.filter_by(id=quiz_id).first_or_404()
#     if quiz.teacher_id == teacher.id:
#         quiz.active ^= 1
#         db.session.commit()
#         return redirect(url_for('teacher.activate_quiz_list'))
#     else:
#         return redirect(url_for('teacher.home'))


@teacher.route('/view_performance_list')
@login_required
def view_performance_list():
    if current_user.teacher is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('student.home'))
    teacher = current_user.teacher
    quiz_list = list(teacher.quiz_created)
    quiz_exists = bool(len(quiz_list))
    return render_template('quiz_list_teacher.html', title='View Performace', quiz_list=quiz_list, quiz_exists=quiz_exists)


@teacher.route('/view_performance/<int:quiz_id>', methods=['POST', 'GET'])
@login_required
def view_performance(quiz_id):
    if current_user.teacher is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('student.home'))

    quiz = Quiz.query.filter_by(id=quiz_id).first_or_404()
    teacher = current_user.teacher

    # Query to fetch the marks obtained by students in the quiz
    marks = db.session.execute(f'SELECT student_id, marks FROM submits_quiz WHERE quiz_id = {quiz_id}').fetchall()

    # Fetching student details and formatting data for API
    listResultScoreModels = []
    for i, entry in enumerate(marks):
        student = Student.query.filter_by(id=entry.student_id).first()
        if student:
            data_entry = {
                'id': student.id,
                'talentName': student.user.name,
                'email': student.user.email,  # Assuming each student.user has an email attribute
                'score': entry.marks
            }
            listResultScoreModels.append(data_entry)

    # Check if there is any data to send or display
    data_exists = bool(listResultScoreModels)

    if request.method == 'POST':
        json_payload = {
            "user": {"id": teacher.id}, 
            "enterpriseJobDetailsModel": {"id": quiz_id},
            "listResultScoreModels": listResultScoreModels
        }

        # Send data to an external API
        api_url = 'api/talentdemandmvp/saveAllTalentscore'  # Placeholder for your API URL
        try:
            response = requests.post(api_url, json=json_payload)
            if response.status_code != 200:
                flash('Failed to upload data to API.', 'error')
            else:
                flash('Data successfully uploaded to API.', 'success')
        except requests.RequestException as e:
            flash(f'Failed to connect to the API: {str(e)}', 'error')

        # Optionally, allow the user to download the results as CSV
        return redirect(url_for('teacher.home'))
    else:
        # Rendering the data to the HTML page for display
        return render_template('view_quiz_performance.html', title="View Performance", quiz_title=quiz.title, data=listResultScoreModels)

