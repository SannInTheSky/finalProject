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