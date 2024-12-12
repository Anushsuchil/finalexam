from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from database import insert_user, insert_request, tounix, fetch_request, is_valid, delete_request, get_time, updated, fetch_teacher,reset_connection
from sql_connection import get_sql_connection
from block import store_hash, retrieve_hash
import random

connection = get_sql_connection()
app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    username = request.form['username']
    password = request.form['password']

    if is_valid(connection, username, role, password):
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher_dashboard', username=username))
        elif role == 'superintendent':
            return redirect(url_for('superintendent_dashboard'))
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('index'))

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/submit_paper', methods=['POST'])
def submit_paper():
    try:
        teacher_id = request.form['teacherId']
        paper_code = request.form['paperCode']
        release_date = request.form['releaseDate']
        release_date = tounix(release_date)
        insert_request(connection, paper_code, release_date, teacher_id)
        flash('Question Paper Submitted Successfully!')
    except Exception as e:
        flash(f'Error submitting paper: {e}')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        user_id = request.form['userId']
        password = request.form['password']
        role = request.form['role']
        insert_user(connection, user_id, role, password)
        flash(f'User {user_id} with role {role} added successfully!')
    except Exception as e:
        flash(f'Error adding user: {e}')
    return redirect(url_for('admin_dashboard'))

@app.route('/teacher_dashboard/')
def teacher_dashboard():
    username = request.args.get('username')  # Get username from query parameters
    if not username:
        flash('Username is required.')
        return redirect(url_for('index'))  # Redirect to login or another appropriate page
    
    # Fetch requests for the teacher
    teacher_requests = fetch_request(connection, username)
    return render_template('teacher_dashboard.html', requests=teacher_requests, username=username)

@app.route('/upload/<username>/<req_id>', methods=['POST'])
def upload_file(username, req_id):
    try:
        if 'pdfFile' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['pdfFile']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and file.filename.endswith('.pdf'):
            filename = f"{username}_{req_id}.pdf"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            release_time = get_time(connection, req_id)
            print('datetime', release_time)
            reset_connection(connection)
            
            updated(connection, req_id, username)
            print("uploaded")
            print("stored in contract")
            
            hashcode = "hasshhhhhhh"
            store_hash(req_id,release_time , hashcode, username)
            print("hash stored")
            
            flash(f'PDF for request {req_id} uploaded successfully!')
            return redirect(url_for('teacher_dashboard', username=username))
        
        flash('Invalid file format. Please upload a PDF.')
    except Exception as e:
        flash(f'Error uploading file: {e}')
    
    return redirect(url_for('teacher_dashboard', username=username))

@app.route('/superintendent_dashboard')
def superintendent_dashboard():
    return render_template('superintendent_dashboard.html')

@app.route('/fetch_pdf/<unique_code>')
def fetch_pdf(unique_code):
    try:
        # Fetch teachers associated with the unique code
        teacher_list = fetch_teacher(connection, unique_code)
        print("techers",teacher_list)
        # Check if any teachers are associated with the code
        if not teacher_list:
            flash('No teachers found for the given code.')
            return "Error: No teachers found.", 404
            exam_id = unique_code
    
        teacher_id = teacher_list[0]
    
        if len(teacher_list) > 1:
            # Randomly select a teacher from the list
            teacher_id = random.choice(teacher_list)
            teacher_list.remove(teacher_id)
            # Delete all requests for this unique code
            for i in teacher_list:
                delete_request(connection, unique_code, i)

        # Retrieve hash for the given code and teacher
        result = retrieve_hash(unique_code, teacher_id)
        print("hash", result)

        # Additional check for invalid result
        if result == "False":
            flash('Invalid unique code.')
            return "Error: Invalid unique code.", 400

        # Check if the hash indicates the paper is ready
        if result != "None":
            filename = f'{unique_code}.pdf'
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Check if the file exists on the server
            if os.path.exists(file_path):
                flash('Question paper downloaded successfully!')
                return send_file(file_path, as_attachment=True)
            
            # File not found on server
            flash('Question paper file not found on the server.')
            return "Error: File not found.", 404
        else:
            # Paper not yet released
            flash('The question paper for the given code has not been released yet.')
            return "Error: Question paper not released yet.", 400
    
    except Exception as e:
        # Log the full error for server-side debugging
        app.logger.error(f'Error fetching PDF: {e}', exc_info=True)
        flash(f'An unexpected error occurred. Please try again later.')
        return "An error occurred.", 500

if __name__ == '__main__':
    app.run(debug=True)
