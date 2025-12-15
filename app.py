from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'cs_elec'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Optional: returns dictionaries
app.config['SECRET_KEY'] = 'your-secret-key-for-jwt'

# Initialize MySQL
mysql = MySQL(app)

# Import routes AFTER initializing mysql
from routes import *

if __name__ == '__main__':
    app.run(debug=True, port=5000)