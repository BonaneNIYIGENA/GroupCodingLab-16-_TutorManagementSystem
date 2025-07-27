import mysql.connector
import datetime
import hashlib
from mysql.connector import Error
from datetime import timedelta
import re


class TutoringSystem:
    def __init__(self):
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None
        self.connection = None
        self.connect_to_database()
        self.init_db()

    def get_db_config(self):
        """Returns database configuration"""
        return {
            'host': 'mysql-1579901e-alustudent-6e44.f.aivencloud.com',
            'port': 25379,
            'user': 'avnadmin',
            'password': 'AVNS_jqnnOJisae0B9tdYVj3',
            'database': 'tms',
            'ssl_disabled': False
        }

    def connect_to_database(self):
        """Establishes database connection and creates database if needed"""
        config = self.get_db_config()

        try:
            # First connect without specifying a database
            temp_connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                ssl_disabled=config['ssl_disabled']
            )

            cursor = temp_connection.cursor()

            # Check if database exists
            cursor.execute(f"SHOW DATABASES LIKE '{config['database']}'")
            result = cursor.fetchone()

            if not result:
                # Create the database if it doesn't exist
                cursor.execute(f"CREATE DATABASE {config['database']}")
                print(f"Created database {config['database']}")

            cursor.close()
            temp_connection.close()

            # Now connect to the specific database
            self.connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                ssl_disabled=config['ssl_disabled']
            )

            print("Successfully connected to database")

        except Error as e:
            print(f"Database connection failed: {e}")
            raise

    def init_db(self):
        """Initializes database tables"""
        try:
            cursor = self.connection.cursor()

            # Create tables if they don't exist
            tables = [
                '''CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(15) PRIMARY KEY,
                    name VARCHAR(25) NOT NULL,
                    email VARCHAR(25) NOT NULL UNIQUE,
                    password_hash VARCHAR(64) NOT NULL
                )''',

                '''CREATE TABLE IF NOT EXISTS tutors (
                    tutor_id VARCHAR(15) PRIMARY KEY,
                    name VARCHAR(25) NOT NULL,
                    email VARCHAR(25) NOT NULL UNIQUE,
                    password_hash VARCHAR(64) NOT NULL
                )''',

                '''CREATE TABLE IF NOT EXISTS session_requests (
                    request_id VARCHAR(10) PRIMARY KEY,
                    student_id VARCHAR(10) NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    details TEXT,
                    request_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )''',

                '''CREATE TABLE IF NOT EXISTS request_participations (
                    request_id VARCHAR(10),
                    student_id VARCHAR(10),
                    PRIMARY KEY (request_id, student_id),
                    FOREIGN KEY (request_id) REFERENCES session_requests(request_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )''',

                '''CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(10) PRIMARY KEY,
                    tutor_id VARCHAR(10) NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    details TEXT,
                    date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    duration INT NOT NULL,
                    end_time TIME NOT NULL,
                    mode VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    from_request BOOLEAN DEFAULT FALSE,
                    request_id VARCHAR(10),
                    location VARCHAR(100),
                    online_link VARCHAR(255),
                    FOREIGN KEY (tutor_id) REFERENCES tutors(tutor_id),
                    FOREIGN KEY (request_id) REFERENCES session_requests(request_id),
                    UNIQUE KEY unique_session_time (date, start_time, tutor_id)
                )''',

                '''CREATE TABLE IF NOT EXISTS registrations (
                    registration_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(10) NOT NULL,
                    session_id VARCHAR(10) NOT NULL,
                    registration_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'registered',
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )''',

                '''CREATE TABLE IF NOT EXISTS session_updates (
                    update_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(10) NOT NULL,
                    field_name VARCHAR(20) NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )''',

                '''CREATE TABLE IF NOT EXISTS cancellations (
                    cancellation_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(10),
                    student_id VARCHAR(10),
                    cancellation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )'''
            ]

            for table in tables:
                cursor.execute(table)

            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"Database initialization failed: {e}")
            raise
