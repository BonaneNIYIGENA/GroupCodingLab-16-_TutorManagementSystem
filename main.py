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

    def hash_password(self, password):
        """Returns SHA-256 hash of the password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_valid_input(self):
        """Prompt for a password with rule-specific feedback and return the hashed password."""
        import re

        def check_password_rules(password: str) -> list:
            errors = []
            if len(password) < 5:
                errors.append("- Must be at least 5 characters")
            if not re.search(r"[A-Z]", password):
                errors.append("- Must include at least one uppercase letter")
            if not re.search(r"[a-z]", password):
                errors.append("- Must include at least one lowercase letter")
            if not re.search(r"\d", password):
                errors.append("- Must include at least one number")
            return errors

        print("\nPassword Requirements:\n- At least 5 characters\n- At least one uppercase letter\n- At least one lowercase letter\n- At least one number\n")

        while True:
            password = input("Enter your password: ").strip()
            errors = check_password_rules(password)
            if not errors:
                return self.hash_password(password)

            print("\n❌ Password does not meet the following criteria:")
            for error in errors:
                print(error)
      
    def get_valid_input_generic(self, prompt, validation_func, error_msg="Invalid input. Please try again."):
        """Generic input validator for any prompt with validation"""
        while True:
            user_input = input(prompt).strip()
            if validation_func(user_input):
                return user_input
            print(error_msg)

    def generate_id(self, entity_type):
        """Generates consistent IDs for entities"""
        prefix_map = {
            'student': ('st_', 'students', 'student_id'),
            'tutor': ('ttr_', 'tutors', 'tutor_id'),
            'session': ('sess_', 'sessions', 'session_id'),
            'request': ('req_', 'session_requests', 'request_id')
        }

        try:
            prefix, table, column = prefix_map[entity_type]
            cursor = self.connection.cursor()

            query = f"SELECT MAX(CAST(SUBSTRING({column}, {len(prefix) + 1}) AS UNSIGNED)) FROM {table}"
            cursor.execute(query)
            max_id = cursor.fetchone()[0]
            new_id_num = (max_id or 0) + 1
            new_id = f"{prefix}{new_id_num:03d}"

            max_length = {'st_': 6, 'ttr_': 7, 'sess_': 8, 'req_': 7}[prefix]
            if len(new_id) > max_length:
                raise ValueError(f"Generated ID exceeds maximum length")

            return new_id

        except Error as e:
            print(f"Error generating ID: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_session_details(self, session_id):
        """Retrieves session details by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT s.*, t.name AS tutor_name, 
                       COUNT(r.student_id) AS registration_count
                FROM sessions s
                JOIN tutors t ON s.tutor_id = t.tutor_id
                LEFT JOIN registrations r ON s.session_id = r.session_id AND r.status = 'registered'
                WHERE s.session_id = %s
                GROUP BY s.session_id
            ''', (session_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving session: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def register_user(self, role):
        """Registers a new user"""
        print(f"\nRegister as a new {role}")
        name = self.get_valid_input_generic("Your Name: ", lambda x: len(x) > 0, "Name cannot be empty.")
        email = self.get_valid_input_generic(
            "Your Email: ",
            lambda x: '@' in x and '.' in x,
            "Please enter a valid email address."
        )
        password_hash = self.get_valid_input()  # calls the password input + validation + hashing

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Check for existing accounts
            cursor.execute('''
                SELECT student_id AS id, 'student' AS role FROM students WHERE email = %s
                UNION
                SELECT tutor_id AS id, 'tutor' AS role FROM tutors WHERE email = %s
            ''', (email, email))

            existing = cursor.fetchall()

            if existing:
                print("\nAccount with this email exists:")
                for acc in existing:
                    print(f"- {acc['role'].capitalize()} ID: {acc['id']}")

                if any(acc['role'] == role for acc in existing):
                    print(f"\nYou already have a {role} account. Please login.")
                    return None

                if input(f"\nRegister as new {role} with this email? (yes/no): ").lower() != 'yes':
                    return None

            # Create new account
            user_id = self.generate_id(role)
            table = 'students' if role == 'student' else 'tutors'
            cursor.execute(
                f"INSERT INTO {table} ({role}_id, name, email, password_hash) VALUES (%s, %s, %s, %s)",
                (user_id, name, email, password_hash)
            )

            self.connection.commit()
            print(f"\nRegistration successful! Your {role} ID is: {user_id}")
            return user_id

        except Error as e:
            print(f"Registration error: {e}")
            self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()