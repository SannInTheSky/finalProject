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

