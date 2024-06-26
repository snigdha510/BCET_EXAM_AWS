from flask import render_template, Blueprint, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from pariksha import db
from pariksha.student.utils import shuffle, random
from pariksha.models import Student, Teacher, Quiz, submits_quiz, User
from pariksha.student.utils import bar_graph
import copy
from sqlalchemy import select
import requests
from sqlalchemy.sql import text
from datetime import datetime
from pariksha import Config
import json

student = Blueprint("student", __name__, url_prefix="/student", template_folder="templates", static_folder="static")

@student.route("/home")
@login_required
def home():
    quotes = ["Let us study things that are no more. It is necessary to understand them, if only to avoid them.",
              "The authority of those who teach is often an obstacle to those who want to learn",
              "To acquire knowledge, one must study; but to acquire wisdom, one must observe."]
    random.shuffle(quotes)
    if current_user.student is None:
        logout_user()
        # return error page ERROR 403
        return "unauthorized access attempted you have been logged out"
    return render_template("student_home.html", quotes=quotes, title="Home")

@student.route("/quiz/<int:job_id>")
@login_required
def quiz(job_id):
    # Fetch the quiz from the database
    quiz = Quiz.query.filter_by(job_id=job_id).first_or_404()

    # Check if the quiz has already been submitted
    if quiz in current_user.student.submitted_quiz:
        flash('You have already submitted this quiz!', 'warning')
        return redirect(url_for('student.home'))

    # Check if the quiz is currently active
    if not quiz.active:
        flash("This quiz is not active at the moment.", "warning")
        return redirect(url_for('student.home'))

    # Shuffle questions and options
    # questions = quiz.questions
    # shuffled_questions = {question.question_desc: random.sample([
    #     question.option_1, question.option_2, question.option_3, question.option_4], k=4)
    #     for question in questions}

    questions = quiz.questions
    qobs = []

    qid = 0
    for question in questions:
        qobs.append({
            'qid': qid,
            'question': question.question_desc,
            'option_1': question.option_1,
            'option_2': question.option_2,
            'option_3': question.option_3,
            'option_4': question.option_4,
        })
        qid += 1

    # Render the quiz directly
    return render_template('quiz.html', title=quiz.title, quiz_id=job_id, qobs=qobs)

@student.route("/quiz/<int:job_id>", methods=["POST"])
@login_required
def quiz_post(job_id):
    quiz = Quiz.query.filter_by(job_id=job_id).first()
    if not quiz.active:
        flash('QUIZ NOT SUBMITTED: The quiz you are trying to submit has expired', 'danger')
        return redirect(url_for('student.home'))
    if quiz in current_user.student.submitted_quiz:
        flash('You have already submitted this quiz!!', 'warning')
        return redirect(url_for('student.home'))

    questions = quiz.questions
    total_marks = 0
    qid = 0
    for question in questions:
        answered = request.form.get(f"question_{qid}")
        correct_option = question.correct_op  # Assuming you have a way to identify the correct answer
        print(f"ANSWERED ===> {answered} | {question.correct_op}")
        marks_awarded = 1 if answered == correct_option else 0
        total_marks += marks_awarded
        qid += 1

    # all_submissions = submits_quiz.query.filter_by(quiz_id=quiz_id).all()
    # all_submissions = db.session.execute(text(f'SELECT * FROM submits_quiz WHERE quiz_id={quiz_id}')).mappings().all()
    # print(f"ALL SUBMISSIONS ======> {all_submissions}")

    # sorted_submissions = sorted(all_submissions, key=lambda x: x.marks, reverse=True)
    # total_submissions = len(sorted_submissions)

    # current_user_percentile = (sum(1 for s in sorted_submissions if s.marks > total_marks) / total_submissions) * 100
    
    
    # submission = submits_quiz(student_id=current_user.student.id, quiz_id=quiz_id, marks=total_marks)
    # submission = submits_quiz.insert().values(student_id=current_user.student.id, quiz_id=quiz_id, marks=total_marks)

    db.session.execute(text(f"INSERT INTO submits_quiz (student_id, quiz_id, marks, time_submitted, terminated, percentile) VALUES ({current_user.student.id}, {quiz.id}, {total_marks}, {datetime.now().year}-{datetime.now().month}-{datetime.now().day}, FALSE, {0.0})"))
    db.session.commit()

    # db.session.add(submission)
    # db.session.commit()

    # Gather additional student details for the API call
    student = User.query.get(current_user.id)
    student_details = {
        "id": student.tid,
        "talentName": student.name,
        "email": student.email,
        "score": total_marks,
        "percentile":0.0
    }

    send_results_to_api(quiz.teacher_id, job_id, [student_details])

    flash(f'Your response for Quiz : {quiz.title} has been submitted', 'success')
    return redirect(url_for('student.home'))


def send_results_to_api(teacher_id, job_id, student_details):
    data = {
        "user": {"id": teacher_id},
        "enterpriseJobDetailsModel": {"id": job_id},
        "listResultScoreModels": student_details
    }
    print('<<<<<<<<send_results_to_api>>>>>>>>>>')
    print(json.dumps(data))
    print('>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<')
    api_url = f'{Config().getBackendURL()}/api/talentdemandmvp/saveAllTalentscore'  # Replace with actual API endpoint
    try:
        response = requests.post(api_url, json=data)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        if response.status_code == 200:
            print("Successfully sent data to API")
        else:
            print(f"Failed to send data with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred while sending results to API: {e}")




@student.route("/list_quiz")
@login_required
def list_quiz():
    if current_user.student is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('teacher.home'))
    teachers_lis = current_user.student.taught_by.all()
    quiz_list = [quiz for teacher in teachers_lis for quiz in teacher.quiz_created]
    quiz_list = [quiz for quiz in quiz_list if quiz.active]
    quiz_exists = bool(len(quiz_list))
    return render_template('quiz_list.html', quiz_list=quiz_list, quiz_exists=quiz_exists, title="Quizzes")


@student.route("/view_performance")
@login_required
def view_performance():
    if current_user.student is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('teacher.home'))
    student = current_user.student
    quiz_submitted_query = tuple(
        db.session.execute(text(f'SELECT * FROM submits_quiz WHERE student_id = {student.id};'))
    )
    quiz_submitted = list()

    for quiz in quiz_submitted_query:
        quiz_title = Quiz.query.filter_by(id=quiz[1]).first().title
        all_marks = list(db.session.execute(text(f'SELECT marks FROM submits_quiz WHERE quiz_id = {quiz[1]}')))
        all_marks = [x[0] for x in all_marks]
        quiz_submitted.append(dict(quiz_title=quiz_title, marks=quiz[3], all_marks=all_marks))
    graph = bar_graph(quiz_submitted)

    return render_template('view_performance.html', graph=graph, title='Your Performance')


@student.route('/view_result')
@login_required
def view_result():
    if current_user.student is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('teacher.home'))
    student = current_user.student
    quiz_submitted_query = tuple(
        db.session.execute(text(f'SELECT * FROM submits_quiz WHERE student_id = {student.id};')))
    quiz_submitted = list()

    for quiz in quiz_submitted_query:
        quiz_title = Quiz.query.filter_by(id=quiz[1]).first().title
        total_marks = Quiz.query.filter_by(id=quiz[1]).first().marks
        quiz_submitted.append(dict(title=quiz_title, marks=quiz[3], total_marks=25))

    quiz_exists = bool(len(quiz_submitted))
    return render_template('view_result.html', quiz_list=quiz_submitted, title="View Result", quiz_exists=quiz_exists)


@student.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.student is None:
        flash('Access Denied', 'danger')
        return redirect(url_for('teacher.home'))
    if request.method == 'GET':
        return render_template('add_teacher.html', title='Add Teacher')
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        teacher = Teacher.query.filter_by(id=teacher_id).first()
        if teacher is None:
            flash(f'Teacher with teacher id {teacher_id} does not exist', 'danger')
            return redirect(url_for('student.add_teacher'))
        if current_user.student in teacher.students:
            flash('The teacher is already added', 'info')
            return redirect(url_for('student.add_teacher'))
        teacher.students.append(current_user.student)
        db.session.commit()
        flash('Teacher has been added', 'success')
        return redirect(url_for('student.add_teacher'))

# @student.route("/quiz/<int:quiz_id>", methods=["GET"])
# def attempt_quiz(quiz_id):
#     # Construct the URL to redirect to
#     url = url_for('student.quiz', quiz_id=quiz_id)
#     # Open a new window with the constructed URL and fullscreen options
#     return f"<script>window.open('{url}', '_blank', 'fullscreen=yes');</script>"
