# tests.py
import unittest
import json
import sys
import os
from app import app

class TestStudentAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and test data"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Test student data
        self.test_student = {
            'name': 'Test Student',
            'course': 'Computer Science',
            'age': 20
        }
        
        # Get authentication token
        response = self.app.post('/api/login',
                                headers={'Authorization': 'Basic YWRtaW46cGFzc3dvcmQ='})  # admin:password
        self.token = json.loads(response.data)['token']
    
    def test_1_create_student(self):
        """Test creating a new student"""
        response = self.app.post('/api/students',
                                data=json.dumps(self.test_student),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.student_id = data['id']  # Save for later tests
    
    def test_2_create_student_validation(self):
        """Test validation for create student"""
        # Test missing name
        invalid_data = {'course': 'CS', 'age': 20}
        response = self.app.post('/api/students',
                                data=json.dumps(invalid_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_3_get_all_students(self):
        """Test getting all students"""
        response = self.app.get('/api/students')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_4_get_single_student(self):
        """Test getting a single student"""
        # First create a student
        create_response = self.app.post('/api/students',
                                       data=json.dumps(self.test_student),
                                       content_type='application/json')
        student_id = json.loads(create_response.data)['id']
        
        # Then get it
        response = self.app.get(f'/api/students/{student_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], self.test_student['name'])
    
    def test_5_get_nonexistent_student(self):
        """Test getting a student that doesn't exist"""
        response = self.app.get('/api/students/99999')
        self.assertEqual(response.status_code, 404)
    
    def test_6_update_student(self):
        """Test updating a student"""
        # Create student
        create_response = self.app.post('/api/students',
                                       data=json.dumps(self.test_student),
                                       content_type='application/json')
        student_id = json.loads(create_response.data)['id']
        
        # Update student
        updated_data = {'name': 'Updated Name', 'age': 21}
        response = self.app.put(f'/api/students/{student_id}',
                               data=json.dumps(updated_data),
                               content_type='application/json',
                               headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['student']['name'], 'Updated Name')
    
    def test_7_update_unauthorized(self):
        """Test updating without authentication"""
        response = self.app.put('/api/students/1',
                               data=json.dumps({'name': 'Test'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)
    
    def test_8_delete_student(self):
        """Test deleting a student"""
        # Create student
        create_response = self.app.post('/api/students',
                                       data=json.dumps(self.test_student),
                                       content_type='application/json')
        student_id = json.loads(create_response.data)['id']
        
        # Delete with confirmation
        response = self.app.delete(f'/api/students/{student_id}?confirm=true',
                                  headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 204)
    
    def test_9_search_students(self):
        """Test search functionality"""
        response = self.app.get('/api/students/search?q=Computer')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)
    
    def test_10_xml_format(self):
        """Test XML format response"""
        response = self.app.get('/api/students?format=xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/xml')
        # Verify it's valid XML
        self.assertIn(b'<?xml', response.data)

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()