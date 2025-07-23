import mysql.connector
import datetime
from typing import Dict, List, Optional, Tuple
from mysql.connector import Error


class TutoringSystem:
    def __init__(self):
        self.current_user_id = None
        self.current_user_role = None
        self.connection = None

        # Connect to database
        self.connect_to_database()

        # Initialize database tables if they don't exist
        self.init_db()

    def connect_to_database(self) -> None:
        """Establish connection to the MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host='mysql-1579901e-alustudent-6e44.f.aivencloud.com',
                port=25379,
                user='avnadmin',
                password='AVNS_jqnnOJisae0B9tdYVj3',
                database='tutor_management_system'
            )

            if self.connection.is_connected():
                print("\nConnection to the database was successful.")
        except Error as e:
            print(f"\nError connecting to MySQL database: {e}")
            raise

    def init_db(self) -> None:
        """Initialize database tables if they don't exist"""
        try:
            cursor = self.connection.cursor()

            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(10) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tutors (
                    tutor_id VARCHAR(10) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_requests (
                    request_id VARCHAR(10) PRIMARY KEY,
                    student_id VARCHAR(10) NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    details TEXT,
                    request_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_participations (
                    request_id VARCHAR(10),
                    student_id VARCHAR(10),
                    PRIMARY KEY (request_id, student_id),
                    FOREIGN KEY (request_id) REFERENCES session_requests(request_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(10) PRIMARY KEY,
                    tutor_id VARCHAR(10) NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    details TEXT,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    mode VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    from_request BOOLEAN DEFAULT FALSE,
                    request_id VARCHAR(10),
                    FOREIGN KEY (tutor_id) REFERENCES tutors(tutor_id),
                    FOREIGN KEY (request_id) REFERENCES session_requests(request_id),
                    UNIQUE KEY unique_session_time (date, time)  # Ensures no duplicate time slots on same date
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS registrations (
                    registration_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(10) NOT NULL,
                    session_id VARCHAR(10) NOT NULL,
                    registration_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'registered',
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_updates (
                    update_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(10) NOT NULL,
                    field_name VARCHAR(20) NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            ''')

            self.connection.commit()
            cursor.close()

        except Error as e:
            print(f"Error initializing database: {e}")
            raise

    # Helper methods
    def get_valid_input(self, prompt: str, validation_func=None, error_msg="Invalid input!! Please try again") -> str:
        """Get validated user input"""
        while True:
            user_input = input(prompt).strip()
            if not validation_func or validation_func(user_input):
                return user_input
            print(error_msg)

    def generate_id(self, prefix: str, table: str) -> str:
        """Generate a new ID with the given prefix"""
        try:
            cursor = self.connection.cursor()
            query = f"SELECT MAX(CAST(SUBSTRING({prefix}_id, {len(prefix) + 2}) AS UNSIGNED)) FROM {prefix}s"
            cursor.execute(query)
            max_id = cursor.fetchone()[0]
            new_id_num = (max_id or 0) + 1
            return f"{prefix}_{new_id_num:03d}"
        except Error as e:
            print(f"Error generating ID: {e}")
            raise

    # User authentication methods
    def register_user(self, role: str) -> Optional[str]:
        """Register a new user (student or tutor)"""
        print(f"\nRegister as a new {role}")
        name = self.get_valid_input("Your Name: ", lambda x: len(x) > 0)
        email = self.get_valid_input("Your Email: ", lambda x: '@' in x and '.' in x)

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Check for existing accounts with this email
            cursor.execute('''
                SELECT student_id AS id, 'student' AS role FROM students WHERE email = %s
                UNION
                SELECT tutor_id AS id, 'tutor' AS role FROM tutors WHERE email = %s
            ''', (email, email))

            existing_accounts = cursor.fetchall()

            if existing_accounts:
                print("\nAn account with this email already exists:")
                for account in existing_accounts:
                    print(f"- {account['role'].capitalize()} ID: {account['id']}")

                if any(account['role'] == role for account in existing_accounts):
                    print(f"\nYou already have a {role} account. Please login instead.")
                    return None

                proceed = input(f"\nDo you want to register as a new {role} with this email? (yes/no): ").lower()
                if proceed != 'yes':
                    return None

            # Create new account
            if role == 'student':
                user_id = self.generate_id('student', 'students')
                cursor.execute(
                    "INSERT INTO students (student_id, name, email) VALUES (%s, %s, %s)",
                    (user_id, name, email)
                )
            else:  # tutor
                user_id = self.generate_id('tutor', 'tutors')
                cursor.execute(
                    "INSERT INTO tutors (tutor_id, name, email) VALUES (%s, %s, %s)",
                    (user_id, name, email)
                )

            self.connection.commit()
            print(f"\nRegistration successful! Your {role} ID is: {user_id}")
            return user_id

        except Error as e:
            print(f"Error during registration: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()

    def login_user(self) -> bool:
        """Authenticate a user"""
        print("\nLogin to your account")
        user_id = input("Enter your ID (st_XXX for student, ttr_XXX for tutor): ").strip()

        try:
            cursor = self.connection.cursor(dictionary=True)

            if user_id.startswith('st_'):
                cursor.execute(
                    "SELECT student_id, name FROM students WHERE student_id = %s",
                    (user_id,)
                )
                user = cursor.fetchone()
                if user:
                    self.current_user_id = user['student_id']
                    self.current_user_role = 'student'
                    print(f"\nWelcome back, student {user['name']}!")
                    return True

            elif user_id.startswith('ttr_'):
                cursor.execute(
                    "SELECT tutor_id, name FROM tutors WHERE tutor_id = %s",
                    (user_id,)
                )
                user = cursor.fetchone()
                if user:
                    self.current_user_id = user['tutor_id']
                    self.current_user_role = 'tutor'
                    print(f"\nWelcome back, tutor {user['name']}!")
                    return True

            print("ID not found. Please try again or register as a new user.")
            return False

        except Error as e:
            print(f"Error during login: {e}")
            return False
        finally:
            cursor.close()

    # Tutor functions
    def tutor_post_session(self) -> None:
        """Tutor posts a new session"""
        print("\nPost a New Tutoring Session")

        session_data = {
            "tutor_id": self.current_user_id,
            "subject": self.get_valid_input("Subject: ", lambda x: len(x) > 0),
            "topic": self.get_valid_input("Topic: ", lambda x: len(x) > 0),
            "level": self.get_valid_input(
                "Level (Beginner/Intermediate/Advanced): ",
                lambda x: x.lower() in ['beginner', 'intermediate', 'advanced']
            ).capitalize(),
            "details": input("Details: "),
            "date": self.get_valid_input(
                "Date (YYYY-MM-DD): ",
                lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-' and
                          datetime.datetime.strptime(x, "%Y-%m-%d") >= datetime.datetime.now()
            ),
            "time": self.get_valid_input(
                "Time (HH:MM): ",
                lambda x: len(x) == 5 and x[2] == ':'
            ),
            "mode": self.get_valid_input(
                "Mode (Online/In-person): ",
                lambda x: x.lower() in ['online', 'in-person']
            ).capitalize(),
            "status": "active"
        }

        try:
            cursor = self.connection.cursor()
            session_id = self.generate_id('sess', 'sessions')

            cursor.execute('''
                INSERT INTO sessions (
                    session_id, tutor_id, subject, topic, level, details, 
                    date, time, mode, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                session_id, session_data['tutor_id'], session_data['subject'],
                session_data['topic'], session_data['level'], session_data['details'],
                session_data['date'], session_data['time'], session_data['mode'],
                session_data['status']
            ))

            self.connection.commit()
            print(f"\nSession posted successfully! Session ID: {session_id}")

        except Error as e:
            print(f"\nError posting session: {e}")
            if "unique_session_time" in str(e):
                print("A session already exists at this date and time. Please choose a different time.")
            self.connection.rollback()
        finally:
            cursor.close()

    def tutor_view_requests(self) -> None:
        """Tutor views pending session requests"""
        print("\nPending Session Requests from Students:")

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Get pending requests with participant counts
            cursor.execute('''
                SELECT sr.request_id, sr.subject, sr.topic, sr.level, sr.details,
                       COUNT(rp.student_id) AS participant_count
                FROM session_requests sr
                LEFT JOIN request_participations rp ON sr.request_id = rp.request_id
                WHERE sr.status = 'pending'
                GROUP BY sr.request_id, sr.subject, sr.topic, sr.level, sr.details
            ''')

            pending_requests = cursor.fetchall()

            if not pending_requests:
                print("No pending session requests.")
                return

            for req in pending_requests:
                print(f"\nRequest ID: {req['request_id']}")
                print(f"Subject: {req['subject']} - {req['topic']}")
                print(f"Level: {req['level']}")
                print(f"Requested by: {req['participant_count']} students")
                print(f"Details: {req['details']}")

                confirm = input("Would you like to confirm this session? (yes/no): ").lower()
                if confirm == 'yes':
                    print("\nPlease provide session details:")
                    session_data = {
                        "tutor_id": self.current_user_id,
                        "subject": req['subject'],
                        "topic": req['topic'],
                        "level": req['level'],
                        "details": req['details'],
                        "date": self.get_valid_input(
                            "Date (YYYY-MM-DD): ",
                            lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-' and
                                      datetime.datetime.strptime(x, "%Y-%m-%d") >= datetime.datetime.now()
                        ),
                        "time": self.get_valid_input(
                            "Time (HH:MM): ",
                            lambda x: len(x) == 5 and x[2] == ':'
                        ),
                        "mode": self.get_valid_input(
                            "Mode (Online/In-person): ",
                            lambda x: x.lower() in ['online', 'in-person']
                        ).capitalize(),
                        "status": "active",
                        "from_request": True,
                        "request_id": req['request_id']
                    }

                    try:
                        # Start transaction
                        cursor.execute("START TRANSACTION")

                        # Create the session
                        session_id = self.generate_id('sess', 'sessions')
                        cursor.execute('''
                            INSERT INTO sessions (
                                session_id, tutor_id, subject, topic, level, details,
                                date, time, mode, status, from_request, request_id
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            session_id, session_data['tutor_id'], session_data['subject'],
                            session_data['topic'], session_data['level'], session_data['details'],
                            session_data['date'], session_data['time'], session_data['mode'],
                            session_data['status'], session_data['from_request'], session_data['request_id']
                        ))

                        # Update request status
                        cursor.execute('''
                            UPDATE session_requests
                            SET status = 'fulfilled'
                            WHERE request_id = %s
                        ''', (req['request_id'],))

                        # Register all participating students
                        cursor.execute('''
                            SELECT student_id FROM request_participations
                            WHERE request_id = %s
                        ''', (req['request_id'],))
                        participants = cursor.fetchall()

                        for participant in participants:
                            cursor.execute('''
                                INSERT INTO registrations (
                                    student_id, session_id, registration_date, status
                                ) VALUES (%s, %s, %s, %s)
                            ''', (
                                participant['student_id'], session_id,
                                datetime.datetime.now().strftime("%Y-%m-%d"), "registered"
                            ))

                        self.connection.commit()
                        print(f"\nSession created successfully! Session ID: {session_id}")
                        print(f"{len(participants)} students have been automatically registered.")

                    except Error as e:
                        self.connection.rollback()
                        print(f"\nError creating session from request: {e}")
                        if "unique_session_time" in str(e):
                            print("A session already exists at this date and time. Please choose a different time.")

        except Error as e:
            print(f"\nError viewing requests: {e}")
        finally:
            cursor.close()

    def tutor_view_scheduled(self) -> None:
        """Tutor views their scheduled sessions"""
        print("\nYour Scheduled Sessions:")

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Get active sessions for this tutor, ordered by date and time
            cursor.execute('''
                SELECT s.session_id, s.subject, s.topic, s.date, s.time, s.mode, s.from_request,
                       COUNT(r.student_id) AS registration_count
                FROM sessions s
                LEFT JOIN registrations r ON s.session_id = r.session_id AND r.status = 'registered'
                WHERE s.tutor_id = %s AND s.status = 'active' AND s.date >= CURDATE()
                GROUP BY s.session_id, s.subject, s.topic, s.date, s.time, s.mode, s.from_request
                ORDER BY s.date, s.time
            ''', (self.current_user_id,))

            tutor_sessions = cursor.fetchall()

            if not tutor_sessions:
                print("You have no scheduled sessions.")
                return

            for session in tutor_sessions:
                print(f"\nSession ID: {session['session_id']}")
                print(f"Subject: {session['subject']} - {session['topic']}")
                print(f"Date: {session['date']} | Time: {session['time']}")
                print(f"Mode: {session['mode']}")
                print(f"Students registered: {session['registration_count']}")
                if session['from_request']:
                    print("This session was created from a student request")

        except Error as e:
            print(f"\nError viewing scheduled sessions: {e}")
        finally:
            cursor.close()

    def tutor_update_session(self) -> None:
        """Tutor updates a session's details"""
        self.tutor_view_scheduled()
        session_id = input("\nEnter the Session ID you want to update (or 'cancel' to go back): ")

        if session_id.lower() == 'cancel':
            return

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Verify session exists and belongs to this tutor
            cursor.execute('''
                SELECT * FROM sessions
                WHERE session_id = %s AND tutor_id = %s
            ''', (session_id, self.current_user_id))

            session = cursor.fetchone()

            if not session:
                print("Invalid Session ID or you don't have permission to update this session.")
                return

            print("\nCurrent session details:")
            print(f"1. Subject: {session['subject']}")
            print(f"2. Topic: {session['topic']}")
            print(f"3. Level: {session['level']}")
            print(f"4. Details: {session['details']}")
            print(f"5. Date: {session['date']}")
            print(f"6. Time: {session['time']}")
            print(f"7. Mode: {session['mode']}")

            field_map = {
                '1': 'subject',
                '2': 'topic',
                '3': 'level',
                '4': 'details',
                '5': 'date',
                '6': 'time',
                '7': 'mode'
            }

            field_choice = input("\nEnter the number of the field you want to update (1-7): ")
            if field_choice not in field_map:
                print("Invalid choice.")
                return

            field = field_map[field_choice]
            new_value = input(f"Enter new {field}: ")

            # Special validation for date and time
            if field == 'date':
                if not (len(new_value) == 10 and new_value[4] == '-' and new_value[7] == '-' and
                        datetime.datetime.strptime(new_value, "%Y-%m-%d") >= datetime.datetime.now()):
                    print("Invalid date format or date is in the past.")
                    return
            elif field == 'time':
                if not (len(new_value) == 5 and new_value[2] == ':'):
                    print("Invalid time format. Use HH:MM.")
                    return

            try:
                # Start transaction
                cursor.execute("START TRANSACTION")

                # Record the update
                cursor.execute('''
                    INSERT INTO session_updates (session_id, field_name, old_value, new_value)
                    VALUES (%s, %s, %s, %s)
                ''', (session_id, field, session[field], new_value))

                # Update the session
                update_query = f"UPDATE sessions SET {field} = %s WHERE session_id = %s"
                cursor.execute(update_query, (new_value, session_id))

                self.connection.commit()
                print(f"\n{field.capitalize()} updated successfully!")

            except Error as e:
                self.connection.rollback()
                print(f"\nError updating session: {e}")
                if "unique_session_time" in str(e):
                    print("A session already exists at this date and time. Please choose a different time.")

        except Error as e:
            print(f"\nError retrieving session: {e}")
        finally:
            cursor.close()

    def tutor_flow(self) -> None:
        """Main tutor menu flow"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT name FROM tutors WHERE tutor_id = %s",
                (self.current_user_id,)
            )
            tutor = cursor.fetchone()

            while True:
                print(f"\nTutor Dashboard - Welcome {tutor['name']}!")
                print("1. Post session")
                print("2. View requested sessions")
                print("3. View scheduled sessions")
                print("4. Session Update")
                print("5. Logout")

                choice = input("Enter your choice (1-5): ")

                if choice == '1':
                    self.tutor_post_session()
                elif choice == '2':
                    self.tutor_view_requests()
                elif choice == '3':
                    self.tutor_view_scheduled()
                elif choice == '4':
                    self.tutor_update_session()
                elif choice == '5':
                    print("Logging out...")
                    self.current_user_id = None
                    self.current_user_role = None
                    break
                else:
                    print("Invalid choice. Please try again.")

        except Error as e:
            print(f"\nError in tutor flow: {e}")
        finally:
            cursor.close()

    # Student functions
    def student_view_available(self) -> None:
        """Student views available sessions"""
        print("\nAvailable Tutoring Sessions:")

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Get active sessions ordered by date and time
            cursor.execute('''
                SELECT s.session_id, s.subject, s.topic, s.level, s.date, s.time, 
                       s.mode, s.details, s.from_request, t.name AS tutor_name
                FROM sessions s
                JOIN tutors t ON s.tutor_id = t.tutor_id
                WHERE s.status = 'active' AND s.date >= CURDATE()
                ORDER BY s.date, s.time
            ''')

            available_sessions = cursor.fetchall()

            if not available_sessions:
                print("No available sessions at this time.")
                return

            for session in available_sessions:
                print(f"\nSession ID: {session['session_id']}")
                print(f"Subject: {session['subject']} - {session['topic']}")
                print(f"Level: {session['level']}")
                print(f"Date: {session['date']} | Time: {session['time']}")
                print(f"Mode: {session['mode']}")
                print(f"Tutor: {session['tutor_name']}")
                print(f"Details: {session['details']}")
                if session['from_request']:
                    print("⭐ This session was created from a student request")

        except Error as e:
            print(f"\nError viewing available sessions: {e}")
        finally:
            cursor.close()

    def student_request_view(self) -> None:
        """Student requests or views session requests"""
        print("\n1. Request new session")
        print("2. View requested sessions")
        sub_choice = input("Enter your choice (1-2): ")

        if sub_choice == '1':
            print("\nRequest a New Session Topic")
            request_data = {
                "student_id": self.current_user_id,
                "subject": self.get_valid_input("Subject: ", lambda x: len(x) > 0),
                "topic": self.get_valid_input("Topic: ", lambda x: len(x) > 0),
                "level": self.get_valid_input(
                    "Level (Beginner/Intermediate/Advanced): ",
                    lambda x: x.lower() in ['beginner', 'intermediate', 'advanced']
                ).capitalize(),
                "details": input("Additional details about what you want to learn: "),
                "request_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "status": "pending"
            }

            try:
                cursor = self.connection.cursor(dictionary=True)

                # Check for existing similar request
                cursor.execute('''
                    SELECT sr.request_id
                    FROM session_requests sr
                    WHERE sr.subject = %s AND sr.topic = %s AND sr.level = %s 
                    AND sr.status = 'pending'
                    LIMIT 1
                ''', (
                    request_data['subject'], request_data['topic'],
                    request_data['level']
                ))

                existing_request = cursor.fetchone()

                if existing_request:
                    # Add participation to existing request
                    try:
                        cursor.execute('''
                            INSERT INTO request_participations (request_id, student_id)
                            VALUES (%s, %s)
                        ''', (existing_request['request_id'], self.current_user_id))

                        self.connection.commit()
                        print("\nSimilar request found! Added your interest to the existing request.")

                        # Get count of participants
                        cursor.execute('''
                            SELECT COUNT(*) AS count
                            FROM request_participations
                            WHERE request_id = %s
                        ''', (existing_request['request_id'],))
                        count = cursor.fetchone()['count']
                        print(f"Now {count} students are interested in this topic.")

                    except Error as e:
                        if "PRIMARY" in str(e):
                            print("You've already participated in this request.")
                        else:
                            raise
                else:
                    # Create new request
                    request_id = self.generate_id('req', 'session_requests')
                    cursor.execute('''
                        INSERT INTO session_requests (
                            request_id, student_id, subject, topic, level, 
                            details, request_date, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        request_id, request_data['student_id'], request_data['subject'],
                        request_data['topic'], request_data['level'], request_data['details'],
                        request_data['request_date'], request_data['status']
                    ))

                    # Add participation
                    cursor.execute('''
                        INSERT INTO request_participations (request_id, student_id)
                        VALUES (%s, %s)
                    ''', (request_id, self.current_user_id))

                    self.connection.commit()
                    print("\nYour session request has been submitted! Tutors will be notified.")

            except Error as e:
                print(f"\nError processing request: {e}")
                self.connection.rollback()
            finally:
                cursor.close()

        elif sub_choice == '2':
            print("\nRequested Sessions (Not yet scheduled):")

            try:
                cursor = self.connection.cursor(dictionary=True)

                # Get pending requests with participation info
                cursor.execute('''
                    SELECT sr.request_id, sr.subject, sr.topic, sr.level, sr.details,
                           COUNT(rp.student_id) AS participant_count,
                           MAX(CASE WHEN rp.student_id = %s THEN 1 ELSE 0 END) AS is_participant
                    FROM session_requests sr
                    LEFT JOIN request_participations rp ON sr.request_id = rp.request_id
                    WHERE sr.status = 'pending'
                    GROUP BY sr.request_id, sr.subject, sr.topic, sr.level, sr.details
                ''', (self.current_user_id,))

                pending_requests = cursor.fetchall()

                if not pending_requests:
                    print("No requested sessions at this time.")
                    return

                for req in pending_requests:
                    print(f"\nRequest ID: {req['request_id']}")
                    print(f"Subject: {req['subject']} - {req['topic']}")
                    print(f"Level: {req['level']}")
                    print(f"Requested by: {req['participant_count']} students")
                    print(f"Details: {req['details']}")

                    if req['is_participant']:
                        print("✅ You have confirmed participation in this request")
                    else:
                        confirm = input("Would you like to confirm participation in this request? (yes/no): ").lower()
                        if confirm == 'yes':
                            try:
                                cursor.execute('''
                                    INSERT INTO request_participations (request_id, student_id)
                                    VALUES (%s, %s)
                                ''', (req['request_id'], self.current_user_id))
                                self.connection.commit()
                                print("Thank you for confirming your interest!")
                            except Error as e:
                                if "PRIMARY" in str(e):
                                    print("You've already participated in this request.")
                                else:
                                    print(f"Error confirming participation: {e}")
                                    self.connection.rollback()

            except Error as e:
                print(f"\nError viewing requests: {e}")
            finally:
                cursor.close()

    def student_register(self) -> None:
        """Student registers for a session"""
        self.student_view_available()
        session_id = input("\nEnter the Session ID you want to register for (or 'cancel' to go back): ")

        if session_id.lower() == 'cancel':
            return

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Verify session exists and is active
            cursor.execute('''
                SELECT session_id FROM sessions
                WHERE session_id = %s AND status = 'active' AND date >= CURDATE()
            ''', (session_id,))

            if not cursor.fetchone():
                print("Invalid Session ID or session is not available.")
                return

            # Check if already registered
            cursor.execute('''
                SELECT registration_id FROM registrations
                WHERE student_id = %s AND session_id = %s AND status = 'registered'
            ''', (self.current_user_id, session_id))

            if cursor.fetchone():
                print("You are already registered for this session.")
                return

            # Register for session
            cursor.execute('''
                INSERT INTO registrations (
                    student_id, session_id, registration_date, status
                ) VALUES (%s, %s, %s, %s)
            ''', (
                self.current_user_id, session_id,
                datetime.datetime.now().strftime("%Y-%m-%d"), "registered"
            ))

            self.connection.commit()
            print("Registration successful!")

        except Error as e:
            print(f"\nError during registration: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def student_view_scheduled(self) -> None:
        """Student views their scheduled sessions"""
        print("\nYour Scheduled Sessions:")

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Get registered sessions ordered by date and time
            cursor.execute('''
                SELECT s.session_id, s.subject, s.topic, s.level, s.date, s.time,
                       s.mode, s.details, r.registration_date, t.name AS tutor_name,
                       NULL AS request_id, NULL AS request_date
                FROM registrations r
                JOIN sessions s ON r.session_id = s.session_id
                JOIN tutors t ON s.tutor_id = t.tutor_id
                WHERE r.student_id = %s AND r.status = 'registered'
                AND s.status = 'active' AND s.date >= CURDATE()

                UNION

                SELECT s.session_id, s.subject, s.topic, s.level, s.date, s.time,
                       s.mode, s.details, NULL AS registration_date, t.name AS tutor_name,
                       sr.request_id, sr.request_date
                FROM request_participations rp
                JOIN session_requests sr ON rp.request_id = sr.request_id
                JOIN sessions s ON sr.request_id = s.request_id
                JOIN tutors t ON s.tutor_id = t.tutor_id
                WHERE rp.student_id = %s AND sr.status = 'fulfilled'
                AND s.status = 'active' AND s.date >= CURDATE()

                ORDER BY date, time
            ''', (self.current_user_id, self.current_user_id))

            scheduled_sessions = cursor.fetchall()

            if not scheduled_sessions:
                print("You have no scheduled sessions.")
                return

            # Get session updates
            cursor.execute('''
                SELECT session_id, field_name, old_value, new_value
                FROM session_updates
                WHERE session_id IN (
                    SELECT session_id FROM (
                        SELECT s.session_id
                        FROM registrations r
                        JOIN sessions s ON r.session_id = s.session_id
                        WHERE r.student_id = %s AND r.status = 'registered'
                        AND s.status = 'active' AND s.date >= CURDATE()

                        UNION

                        SELECT s.session_id
                        FROM request_participations rp
                        JOIN session_requests sr ON rp.request_id = sr.request_id
                        JOIN sessions s ON sr.request_id = s.request_id
                        WHERE rp.student_id = %s AND sr.status = 'fulfilled'
                        AND s.status = 'active' AND s.date >= CURDATE()
                    ) AS session_ids
                )
                ORDER BY update_timestamp
            ''', (self.current_user_id, self.current_user_id))

            updates = {}
            for update in cursor.fetchall():
                if update['session_id'] not in updates:
                    updates[update['session_id']] = []
                updates[update['session_id']].append(update)

            # Display sessions
            for session in scheduled_sessions:
                if session['request_id']:
                    print("\n⭐ Confirmed Request Session:")
                    print(f"Request ID: {session['request_id']}")
                    print(f"Session ID: {session['session_id']}")
                    print(f"Original Request Date: {session['request_date']}")
                else:
                    print("\nRegistered Session:")
                    print(f"Session ID: {session['session_id']}")
                    print(f"Registration Date: {session['registration_date']}")

                print(f"Subject: {session['subject']} - {session['topic']}")
                print(f"Level: {session['level']}")
                print(f"Date: {session['date']} | Time: {session['time']}")
                print(f"Mode: {session['mode']}")
                print(f"Tutor: {session['tutor_name']}")
                print(f"Details: {session['details']}")

                if session['session_id'] in updates:
                    print("\nUpdates:")
                    for update in updates[session['session_id']]:
                        print(
                            f"- {update['field_name'].capitalize()} changed from '{update['old_value']}' to '{update['new_value']}'")

        except Error as e:
            print(f"\nError viewing scheduled sessions: {e}")
        finally:
            cursor.close()

    def run(self) -> None:  # Make sure this is properly indented inside the class
        """Main system loop"""
        print("\nWelcome to Tutoring Management System!")

        while True:
            print("\nMain Menu")
            print("1. Login")
            print("2. Create new account")
            print("3. Exit System")

            choice = input("Enter your choice (1-3): ")

            if choice == '1':
                if self.login_user():
                    if self.current_user_role == 'student':
                        self.student_flow()
                    else:
                        self.tutor_flow()

    def student_flow(self) -> None:
        """Main student menu flow"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT name FROM students WHERE student_id = %s",
                (self.current_user_id,)
            )
            student = cursor.fetchone()

            while True:
                print(f"\nStudent Dashboard - Welcome {student['name']}!")
                print("1. View available sessions")
                print("2. Request/view requested sessions")
                print("3. Session registration")
                print("4. View all scheduled sessions")
                print("5. Logout")

                choice = input("Enter your choice (1-5): ")

                if choice == '1':
                    self.student_view_available()
                elif choice == '2':
                    self.student_request_view()
                elif choice == '3':
                    self.student_register()
                elif choice == '4':
                    self.student_view_scheduled()
                elif choice == '5':
                    print("Logging out...")
                    self.current_user_id = None
                    self.current_user_role = None
                    break
                else:
                    print("Invalid choice. Please try again.")

        except Error as e:
            print(f"\nError in student flow: {e}")
        finally:
            cursor.close()

        # Main system flow
        def run(self) -> None:
            """Main system loop"""

        print("\nWelcome to Tutoring Management System!")

        while True:
            print("\nMain Menu")
            print("1. Login")
            print("2. Create new account")
            print("3. Exit System")

            choice = input("Enter your choice (1-3): ")

            if choice == '1':
                if self.login_user():  # Fixed: Added parentheses and proper method call
                    if self.current_user_role == 'student':
                        self.student_flow()
                    else:
                        self.tutor_flow()
            elif choice == '2':
                print("\nCreate New Account")
                print("1. Register as Student")
                print("2. Register as Tutor")
                print("3. Back to main menu")

                reg_choice = input("Enter your choice (1-3): ")

                if reg_choice == '1':
                    user_id = self.register_user('student')
                    if user_id:
                        self.current_user_id = user_id
                        self.current_user_role = 'student'
                        self.student_flow()
                elif reg_choice == '2':
                    user_id = self.register_user('tutor')
                    if user_id:
                        self.current_user_id = user_id
                        self.current_user_role = 'tutor'
                        self.tutor_flow()
                elif reg_choice == '3':
                    continue
                else:
                    print("Invalid choice. Please try again.")
            elif choice == '3':
                print("\nThank you for using the Tutoring Management System. Goodbye!")
                if self.connection and self.connection.is_connected():
                    self.connection.close()
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        system = TutoringSystem()
        system.run()
    except Error as e:
        print(f"\nA critical error occurred: {e}")
        print("The system will now exit.")
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
    finally:
        print("Goodbye!")