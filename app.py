from flask import Flask, render_template, request, redirect, url_for, flash
# from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask import session
import random
from werkzeug.security import generate_password_hash
from datetime import datetime
import string


app = Flask(__name__)
app.secret_key = 'shruti'  # Set this to a random value for security


# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Shruti%402004@localhost/quizManagementSystem'  # Update password and DB name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Admin Model
class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Increased size

# Student Model
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Increased size

# Quiz Model
class Quiz(db.Model):
    quiz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), nullable=False)
    quiz_code = db.Column(db.String(6), unique=True, nullable=False)  # New column for the unique 6-digit code
    teacher = db.relationship('Teacher', backref='teacher_quizzes', lazy=True)  # Change backref name

    def __repr__(self):
        return f"<Quiz {self.quiz_name}>"

# Teacher Model
class Teacher(db.Model):
    teacher_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Increased size
    quizzes = db.relationship('Quiz', backref='teacher_relation', lazy=True)  # Keep this as is or change it as well

# Question Model
class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)  # 1/2/3/4

# Answer Model
class Answer(db.Model):
    answer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    option_marked = db.Column(db.Integer, nullable=False)  # 1/2/3/4
    correct_option = db.Column(db.Integer, nullable=False)

# Result Model
class Result(db.Model):
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id', ondelete='CASCADE'), nullable=False)
    total_correct = db.Column(db.Integer, nullable=False)
    total_incorrect = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Integer, nullable=False)

# Home
@app.route('/')
def home():
    return render_template('home.html')

# Route for About Us page
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Fetch the user based on the role and email
        user = None  # Initialize user variable

        if role == 'admin':
            user = Admin.query.filter_by(email=email).first()
        elif role == 'teacher':
            user = Teacher.query.filter_by(email=email).first()
            if user:
                session['teacher_id'] = user.teacher_id
        elif role == 'student':
            user = Student.query.filter_by(email=email).first()
            if user:
                session['student_id'] = user.student_id
        else:
            flash('Invalid role selected!', 'danger')
            return redirect(url_for('login'))

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # Session management: Store user info in session
            if role == 'admin':
                session['user_id'] = user.admin_id  # Use admin_id instead of id
            elif role == 'teacher':
                session['user_id'] = user.teacher_id  # Use teacher_id
            elif role == 'student':
                session['user_id'] = user.student_id  # Use student_id

            session['role'] = role

            # Redirect based on role
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif role == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route for Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    quizzes = Quiz.query.all()  # Get all quizzes created by any teacher
    return render_template('admin_dashboard.html', quizzes=quizzes)


# Route for Teacher Dashboard
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'role' in session and session['role'] == 'teacher':
        quizzes = Quiz.query.filter_by(teacher_id=session['user_id']).all()
        return render_template('teacher_dashboard.html', quizzes=quizzes)
    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))


# Route for Student Dashboard
@app.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    student_id = session['student_id']
    student = Student.query.get(student_id)
    batch = student.batch

    # Get open quizzes for the student's batch
    quizzes = Quiz.query.filter(
        Quiz.start_date <= datetime.now(),
        Quiz.end_date >= datetime.now(),
        # Quiz.batch == batch
    ).all()

    return render_template('student_dashboard.html', quizzes=quizzes, username=student.name)


# Route to display the registration form
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists in the Admin table
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            flash("Admin with this email already exists!", 'danger')
            return redirect(url_for('register'))  # Redirect back to register page

        # If no existing admin, create a new Admin account
        new_admin = Admin(name=name, email=email, password=generate_password_hash(password))
        db.session.add(new_admin)
        db.session.commit()

        flash("Admin account created successfully! You can now log in.", 'success')
        return redirect(url_for('login'))  # Redirect to login page

    return render_template('register.html')

@app.route('/accounts')
def accounts():
    teachers = Teacher.query.all()  # Get all teacher accounts
    students = Student.query.all()  # Get all student accounts
    created_account = None  # Include this variable if you want to show a flash message for successful account creation
    return render_template('accounts.html', teachers=teachers, students=students, created_account=created_account)

@app.route('/admin/create_student_account', methods=['GET', 'POST'])
def create_student_account():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            full_name = request.form['full_name']
            enrollment_number = request.form['enrollment_number']
            batch = request.form['batch']
            email = request.form['email']
            password = request.form['password']
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            if Student.query.filter_by(email=email).first():
                flash("Email already exists!", "danger")
                return redirect(url_for('create_student_account'))

            new_student = Student(name=full_name, student_id=enrollment_number, batch=batch, email=email, password=hashed_password)
            db.session.add(new_student)
            db.session.commit()

            flash("Student account created successfully!", "success")
            return redirect(url_for('accounts'))

        return render_template('create_student_account.html')

    return redirect(url_for('login'))

@app.route('/admin/create_teacher_account', methods=['GET', 'POST'])
def create_teacher_account():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            print(request.form)  # This will show the form data in your console/log
            name = request.form.get('name')
            employee_number = request.form.get('employee_number')
            email = request.form.get('email')
            password = request.form.get('password')

            # Check if any of the fields are missing
            if not name or not employee_number or not email or not password:
                flash("All fields are required!", "danger")
                return redirect(url_for('create_teacher_account'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            if Teacher.query.filter_by(email=email).first():
                flash("Email already exists!", "danger")
                return redirect(url_for('create_teacher_account'))

            new_teacher = Teacher(
                name=name,
                teacher_id=employee_number,  # Using employee_number as teacher_id
                email=email,
                password=hashed_password
            )
            db.session.add(new_teacher)
            db.session.commit()
            flash("Teacher account created successfully!", "success")
            return redirect(url_for('accounts'))

        return render_template('create_teacher_account.html')

    flash("Unauthorized access!", "danger")
    return redirect(url_for('login'))


# Create Quiz Route
@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form.get('quiz_name')
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')

        # Generate a unique code
        quiz_code = generate_unique_code()

        teacher_id = session['user_id']

        new_quiz = Quiz(
            quiz_code=quiz_code,
            quiz_name=quiz_name,
            start_date=start_date,
            end_date=end_date,
            teacher_id=teacher_id
        )
        db.session.add(new_quiz)
        db.session.commit()

        flash(f"Quiz created successfully! Your quiz code is: {quiz_code}", "success")
        return redirect(url_for('add_question', quiz_id=new_quiz.quiz_id))  # Redirect to add questions

    return render_template('create_quiz.html')

# Function to generate a unique 6-digit code
def generate_unique_code():
    return ''.join(random.choices(string.digits, k=6))

# Function to check if the generated code is unique
def is_code_unique(code):
    return Quiz.query.filter_by(quiz_code=code).first() is None


# Create Question for Quiz Route
@app.route('/add_question/<quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if request.method == 'POST':
        question_text = request.form['question_text']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']

        # Create a new question
        new_question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_answer=correct_answer
        )
        db.session.add(new_question)
        db.session.commit()

        flash("Question added successfully!", "success")

        # Fetch all questions for the quiz and pass them to the template
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return render_template('add_question.html', quiz=quiz, questions=questions)

    # If the method is GET, simply render the page with existing questions
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('add_question.html', quiz=quiz, questions=questions)


@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    # Retrieve the quiz and check if the logged-in teacher is the creator
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if quiz.teacher_id != session['teacher_id']:
        flash("You are not authorized to delete this quiz.", "danger")
        return redirect(url_for('teacher_dashboard'))

    # Step 1: Delete answers related to the quiz by deleting answers for each question in the quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    for question in questions:
        Answer.query.filter_by(question_id=question.question_id).delete()

    # Step 2: Delete results related to the quiz
    Result.query.filter_by(quiz_id=quiz_id).delete()

    # Step 3: Delete questions related to the quiz
    Question.query.filter_by(quiz_id=quiz_id).delete()

    # Step 4: Delete the quiz itself
    db.session.delete(quiz)
    db.session.commit()

    flash('Quiz and all related data have been deleted successfully!', 'success')
    return redirect(url_for('teacher_dashboard'))

# Route for joining a quiz with code (this is for entering a quiz code)
@app.route('/join_quiz', methods=['GET', 'POST'])
def join_quiz():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    if request.method == 'POST':
        quiz_code = request.form.get('quiz_code')  # Get the quiz code entered by the student
        
        # Look up the quiz using the provided code
        quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
        
        if quiz:
            # Redirect to the quiz attempt page
            return redirect(url_for('attempt_quiz', quiz_id=quiz.id))
        else:
            flash('Invalid Quiz Code. Please try again.', 'danger')
            return redirect(url_for('join_quiz'))  # Redirect to the same page with a flash message
    
    return render_template('join_quiz_with_code.html')


# Route for directly joining the quiz by quiz_id
@app.route('/join_quiz/<int:quiz_id>', methods=['GET'])
def join_quiz_by_id(quiz_id):
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    # Fetch quiz details and the questions
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    # Pass quiz data to the template
    return render_template('join_quiz.html', quiz=quiz, questions=questions)

@app.route('/join_quiz_with_code', methods=['GET', 'POST'])
def join_quiz_with_code():
    if request.method == 'POST':
        quiz_code = request.form['quiz_code']
        # Look for the quiz using the quiz code
        quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
        
        if quiz:
            # Check if the student is allowed to join the quiz, e.g., based on batch or other conditions
            student = Student.query.filter_by(email=session.get('email')).first()  # Assuming student is logged in
            if student and student.batch == quiz.batch:  # Example condition
                # Redirect to the quiz page
                return redirect(url_for('take_quiz', quiz_id=quiz.quiz_id))
            else:
                flash('You are not eligible to join this quiz.', 'danger')
        else:
            flash('Quiz not found. Please check the code and try again.', 'danger')

    return render_template('join_quiz_with_code.html') 

# Route for attempting the quiz
@app.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    # Fetch quiz and its questions
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.quiz_id).all()

    if request.method == 'POST':
        # Store answers in the Answer table
        student_id = session['student_id']
        total_correct = 0
        for question in questions:
            answer = request.form.get(f'question_{question.id}')
            correct_answer = question.correct_answer
            if answer == correct_answer:
                total_correct += 1

            # Save each answer
            answer_record = Answer(
                student_id=student_id,
                question_id=question.id,
                option_marked=answer,
                correct_option=correct_answer
            )
            db.session.add(answer_record)

        db.session.commit()

        # Calculate score and store the result
        result = Result.query.filter_by(student_id=student_id, quiz_id=quiz.id).first()
        if not result:
            result = Result(student_id=student_id, quiz_id=quiz.id, total_correct=total_correct, total_incorrect=len(questions) - total_correct, total_score=total_correct)
            db.session.add(result)
        else:
            result.total_correct = total_correct
            result.total_incorrect = len(questions) - total_correct
            result.total_score = total_correct

        db.session.commit()

        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)

# Route for submitting the quiz
@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    # Fetch the quiz and questions
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Get the student ID (assuming it's stored in the session)
    student_id = session.get('student_id')  # Ensure the student is logged in

    if not student_id:
        flash('You must be logged in to submit a quiz.', 'danger')
        return redirect(url_for('login'))  # Redirect to login if no student is logged in

    total_correct = 0
    total_incorrect = 0
    total_questions = len(questions)  # Total number of questions in the quiz

    # Option mapping for the radio button values
    option_map = {'option1': 1, 'option2': 2, 'option3': 3, 'option4': 4}

    # Loop through each question and get the student's answer
    for question in questions:
        # Get the student's answer from the form (using the question ID in the form name)
        student_answer = request.form.get(f'question_{question.question_id}')
        
        if student_answer:
            # Map the student answer (e.g., 'option1') to the corresponding integer value
            student_answer_int = option_map.get(student_answer)

            # Ensure the answer is valid
            if student_answer_int is not None:
                # Compare the student's answer with the correct answer
                correct_answer = question.correct_answer
                if student_answer_int == correct_answer:
                    total_correct += 1
                else:
                    total_incorrect += 1

                # Save the student's answer in the Answer table
                answer_record = Answer(
                    student_id=student_id,
                    question_id=question.question_id,
                    option_marked=student_answer_int,  # Save the integer value here
                    correct_option=correct_answer
                )
                db.session.add(answer_record)
            else:
                flash(f"Invalid answer for question {question.question_id}. Please select a valid option.", 'danger')
                return redirect(url_for('submit_quiz', quiz_id=quiz_id))  # Return if answer is invalid

    # Calculate total score (percentage)
    if total_questions > 0:
        total_score = (total_correct / total_questions) * 100  # Calculate the percentage
    else:
        total_score = 0  # Avoid division by zero if no questions exist

    # Store the result in the Result table
    result = Result.query.filter_by(student_id=student_id, quiz_id=quiz_id).first()
    if not result:
        result = Result(
            student_id=student_id,
            quiz_id=quiz_id,
            total_correct=total_correct,
            total_incorrect=total_incorrect,
            total_score=total_score  # Store the percentage in total_score
        )
        db.session.add(result)
    else:
        # If the result already exists, update it
        result.total_correct = total_correct
        result.total_incorrect = total_incorrect
        result.total_score = total_score  # Update the percentage in total_score

    # Commit the changes to the database
    db.session.commit()

    # Show a success message and redirect to the dashboard or results page
    flash('Quiz submitted successfully!', 'success')
    return redirect(url_for('student_dashboard'))  # Redirect to dashboard or another page

def calculate_score(student, quiz):
    # Example function to calculate score based on student's answers
    correct_answers = 0
    for question in quiz.questions:
        answer = request.form.get(str(question.id))  # Assume answers are posted by question ID
        if answer == question.correct_answer:
            correct_answers += 1
    return correct_answers

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/verify_quiz_code', methods=['POST'])
def verify_quiz_code():
    quiz_code = request.form['quiz_code']
    quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()

    if quiz:
        return redirect(url_for('attempt_quiz', quiz_id=quiz.quiz_id))
    else:
        flash('Invalid Quiz Code. Please try again.', 'danger')
        return redirect(url_for('join_quiz_with_code'))

@app.route('/quiz_results/<int:quiz_id>')
def quiz_results(quiz_id):
    # Fetch the quiz details
    quiz = Quiz.query.get_or_404(quiz_id)

    # Fetch the results for the quiz
    results = db.session.query(
        Result.total_correct,
        Result.total_incorrect,
        Result.total_score,
        Student.email.label('student_email')
    ).join(Student, Student.student_id == Result.student_id)\
     .filter(Result.quiz_id == quiz_id).all()

    # Render the results page with the results
    return render_template('quiz_results.html', quiz_id=quiz_id, results=results)


def init_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)
