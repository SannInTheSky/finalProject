# setup_database.py
import mysql.connector

def setup_database():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS cs_elec")
        cursor.execute("USE cs_elec")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create students table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                course VARCHAR(50) NOT NULL,
                age INT CHECK (age >= 16 AND age <= 60)
            )
        """)
        
        print("Database setup completed successfully!")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error setting up database: {e}")

if __name__ == '__main__':
    setup_database()