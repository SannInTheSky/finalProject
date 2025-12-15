# app.py
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'cs_elec'
app.config['SECRET_KEY'] = 'your-secret-key-for-jwt'

# Initialize MySQL
mysql = MySQL(app)

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# ==================== WEB PAGES ====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/students')
def students_page():
    try:
        cursor = mysql.connection.cursor()
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
        
        return render_template('students.html', students=student_list)
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

@app.route('/login')
def login_page():
    return render_template('login.html')