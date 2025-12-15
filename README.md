# Student Management REST API
A complete Flask-based REST API with web interface for managing student records. Features CRUD operations, JWT authentication, XML/JSON format support, and a responsive web interface.

📋 Features
✅ Full CRUD Operations (Create, Read, Update, Delete)

✅ JWT Authentication for secure API access

✅ Web Interface with responsive design

✅ User Registration & Login System

✅ XML/JSON Format Support

✅ Search Functionality

✅ MySQL Database Integration

✅ Comprehensive Unit Testing

✅ RESTful API Design

📦 Installation & Setup
Step 1: Clone & Navigate
bash
git clone https://github.com/yourusername/student-api.git
cd student-api
Step 2: Create Virtual Environment
bash
# Create virtual environment
python -m venv venv

Step 3: Install Dependencies
bash
pip install -r requirements.txt

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

requirements.txt contains:
text
Flask==2.3.3
Flask-MySQLdb==1.0.1
PyMySQL==1.0.3
PyJWT==2.8.0
dicttoxml==1.7.16
bcrypt==4.0.1
