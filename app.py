# app.py - MINIMAL VERSION
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-sessions'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'cs_elec'
app.config['SECRET_KEY'] = 'your-secret-key-for-jwt'

mysql = MySQL(app)

# Import ALL routes from routes.py
from routes import *

if __name__ == '__main__':
    app.run(debug=True, port=5000)