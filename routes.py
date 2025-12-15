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
    
# Update student by ID
@app.route('/api/students/<int:student_id>', methods=['PUT'])
@token_required  # JWT authentication decorator
def update_student(student_id):
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
@token_required  # JWT authentication decorator
def delete_student(student_id):
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