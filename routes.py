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