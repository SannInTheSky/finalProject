# routes.py
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
import jwt
from functools import wraps
from datetime import datetime, timedelta
import bcrypt

from app import app, mysql

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
            
            if user and check_password(user[2], password):
                token = jwt.encode({
                    'user_id': user[0],
                    'username': user[1],
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }, app.config['SECRET_KEY'])
                
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
        confirm_password = request.form.get('confirm_password')
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
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
            
            # Hash password and insert user WITHOUT email
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
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

# ==================== REST OF YOUR API ROUTES ====================
# Keep your existing API routes below...
# JWT decorator, login API, CRUD operations, etc.

# ==================== JWT Authentication Decorator ====================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if 'Bearer' in auth_header:
                token = auth_header.split()[1]
            else:
                token = auth_header
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ==================== API AUTH ENDPOINT ====================
@app.route('/api/login', methods=['POST'])
def api_login():
    """Generate JWT token"""
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return jsonify({'error': 'Login required'}), 401
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (auth.username,))
        user = cursor.fetchone()
        
        if user and check_password(user[2], auth.password):
            token = jwt.encode({
                'user': auth.username,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, app.config['SECRET_KEY'])
            
            return jsonify({'token': token}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid credentials'}), 401

# ==================== API CRUD ENDPOINTS ====================
@app.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json()
    
    # Validation
    if not data.get('name') or not data['name'].strip():
        return jsonify({'error': 'Name is required and cannot be empty'}), 400
    
    if not data.get('course') or not data['course'].strip():
        return jsonify({'error': 'Course is required'}), 400
    
    # Age validation
    try:
        age = int(data.get('age', 0))
        if not 16 <= age <= 60:
            return jsonify({'error': 'Age must be between 16 and 60'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Age must be a valid integer'}), 400
    
    # Insert into database
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO students (name, course, age) VALUES (%s, %s, %s)",
                   (data['name'].strip(), data['course'].strip(), age))
    mysql.connection.commit()
    
    return jsonify({'message': 'Student created', 'id': cursor.lastrowid}), 201

# ... rest of your API routes ...

# Get all students
@app.route('/api/students', methods=['GET'])
def get_all_students():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        
        # Format as list of dictionaries
        student_list = []
        for student in students:
            student_list.append({
                'id': student[0],
                'name': student[1],
                'course': student[2],
                'age': student[3]
            })
        
        format_type = request.args.get('format', 'json')
        
        if format_type == 'xml':
            return json_to_xml(student_list), 200, {'Content-Type': 'application/xml'}
        else:
            return jsonify(student_list), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get single student by ID
@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        student_data = {
            'id': student[0],
            'name': student[1],
            'course': student[2],
            'age': student[3]
        }
        
        format_type = request.args.get('format', 'json')
        
        if format_type == 'xml':
            return json_to_xml(student_data), 200, {'Content-Type': 'application/xml'}
        else:
            return jsonify(student_data), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update student by ID
@app.route('/api/students/<int:student_id>', methods=['PUT'])
@token_required
def update_student(current_user, student_id):
    try:
        data = request.get_json()
        
        # Check if student exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Student not found'}), 404
        
        # Build dynamic update query based on provided fields
        updates = []
        values = []
        
        if 'name' in data:
            if not data['name'] or not data['name'].strip():
                return jsonify({'error': 'Name cannot be empty'}), 400
            updates.append("name = %s")
            values.append(data['name'].strip())
        
        if 'course' in data:
            if not data['course'] or not data['course'].strip():
                return jsonify({'error': 'Course cannot be empty'}), 400
            updates.append("course = %s")
            values.append(data['course'].strip())
        
        if 'age' in data:
            try:
                age = int(data['age'])
                if not 16 <= age <= 60:
                    return jsonify({'error': 'Age must be between 16 and 60'}), 400
                updates.append("age = %s")
                values.append(age)
            except (ValueError, TypeError):
                return jsonify({'error': 'Age must be a valid integer'}), 400
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Add student_id to values
        values.append(student_id)
        
        # Execute update
        query = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, values)
        mysql.connection.commit()
        
        # Get updated student data
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        updated_student = cursor.fetchone()
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': {
                'id': updated_student[0],
                'name': updated_student[1],
                'course': updated_student[2],
                'age': updated_student[3]
            }
        }), 200
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500

# Delete student by ID
@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@token_required
def delete_student(current_user, student_id):
    try:
        cursor = mysql.connection.cursor()
        
        # Check if student exists
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Optional: Check for confirm parameter
        confirm = request.args.get('confirm', 'false').lower()
        if confirm != 'true':
            return jsonify({
                'message': 'Add ?confirm=true to confirm deletion',
                'student': {
                    'id': student[0],
                    'name': student[1],
                    'course': student[2],
                    'age': student[3]
                }
            }), 200
        
        # Delete the student
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        mysql.connection.commit()
        
        # Check if deletion was successful
        if cursor.rowcount > 0:
            return '', 204  # No Content on successful deletion
        else:
            return jsonify({'error': 'Deletion failed'}), 500
            
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500

# Search students
@app.route('/api/students/search', methods=['GET'])
def search_students():
    search_term = request.args.get('q', '')
    
    if not search_term:
        return jsonify({'error': 'Search query parameter "q" is required'}), 400
    
    try:
        cursor = mysql.connection.cursor()
        # Search in name and course fields
        cursor.execute(
            "SELECT * FROM students WHERE name LIKE %s OR course LIKE %s",
            (f'%{search_term}%', f'%{search_term}%')
        )
        students = cursor.fetchall()
        
        # Format results
        student_list = []
        for student in students:
            student_list.append({
                'id': student[0],
                'name': student[1],
                'course': student[2],
                'age': student[3]
            })
        
        # Check format parameter
        format_type = request.args.get('format', 'json')
        
        if format_type == 'xml':
            return json_to_xml({
                'search_term': search_term,
                'results': student_list,
                'count': len(student_list)
            }), 200, {'Content-Type': 'application/xml'}
        else:
            return jsonify({
                'search_term': search_term,
                'results': student_list,
                'count': len(student_list)
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500