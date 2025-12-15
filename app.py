# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import bcrypt
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-sessions'  # For flash messages

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'cs_elec'
app.config['SECRET_KEY'] = 'your-secret-key-for-jwt'

# Initialize MySQL
mysql = MySQL(app)

# Import routes
from routes import *

# ==================== HELPER FUNCTIONS ====================
def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password, user_password):
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ==================== WEB PAGES ====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/students')
def students_page():
    """Students list page with search"""
    search_query = request.args.get('q', '')
    
    try:
        cursor = mysql.connection.cursor()
        
        if search_query:
            # Search in name or course
            cursor.execute(
                "SELECT * FROM students WHERE name LIKE %s OR course LIKE %s",
                (f'%{search_query}%', f'%{search_query}%')
            )
        else:
            cursor.execute("SELECT * FROM students")
        
        students = cursor.fetchall()
        
        student_list = []
        for student in students:
            student_list.append({
                'id': student[0],
                'name': student[1],
                'course': student[2],
                'age': student[3]
            })
        
        return render_template('students.html', 
                              students=student_list, 
                              search_query=search_query)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/students/create')
def create_page():
    return render_template('create.html')

@app.route('/students/<int:student_id>/edit')
def edit_student_page(student_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return "Student not found", 404
        
        student_data = {
            'id': student[0],
            'name': student[1],
            'course': student[2],
            'age': student[3]
        }
        
        return render_template('update.html', student=student_data)
    except Exception as e:
        return str(e), 500

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password(user[2], password):  # user[2] is password field
                # Generate JWT token
                token = jwt.encode({
                    'user_id': user[0],
                    'username': user[1],
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }, app.config['SECRET_KEY'])
                
                # Store token in session
                session['jwt_token'] = token
                session['username'] = username
                
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
                
        except Exception as e:
            flash('Login error: ' + str(e), 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        try:
            cursor = mysql.connection.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists', 'danger')
                return render_template('register.html')
            
            # Check if email exists
            if email:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already registered', 'danger')
                    return render_template('register.html')
            
            # Hash password and insert user
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )
            mysql.connection.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login_page'))
            
        except Exception as e:
            flash('Registration error: ' + str(e), 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)