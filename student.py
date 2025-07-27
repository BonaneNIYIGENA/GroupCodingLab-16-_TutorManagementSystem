import datetime
from getpass import getpass
from mysql.connector import Error

"""
   Function that allows displays the student dashboard interface
 """
def student_flow(system):
    """Student dashboard with direct session viewing/registration"""
    while True:
        print(f"\n🎓 Student Dashboard - Welcome {system.current_user_name}!")
        print("1. View/Register for Available Sessions")
        print("2. Manage Requests")
        print("3. My Schedule - View/Cancel")
        print("4. Logout")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            student_view_and_register_sessions(system)
        elif choice == '2':
            student_requests_menu(system)
        elif choice == '3':
            student_schedule_menu(system)
        elif choice == '4':
            print("Logging out...")
            system.current_user_id = None
            system.current_user_role = None
            system.current_user_name = None
            break
        else:
            print("Invalid choice. Please enter a number between 1-4.")
def register_for_session(system, session):
    """Handles session registration process with time collision check"""
    try:
        cursor = system.connection.cursor(dictionary=True)

        # Check if already registered
        cursor.execute('''
            SELECT 1 FROM registrations 
            WHERE student_id = %s AND session_id = %s AND status = 'registered'
        ''', (system.current_user_id, session['session_id']))

        if cursor.fetchone():
            print("\n⚠️ You are already registered for this session!")
            return False

        # Check for time conflicts
        cursor.execute('''
            SELECT s.session_id, s.subject, s.start_time, s.end_time
            FROM registrations r
            JOIN sessions s ON r.session_id = s.session_id
            WHERE r.student_id = %s 
            AND s.date = %s 
            AND (
                (s.start_time < %s AND s.end_time > %s) OR
                (s.start_time >= %s AND s.start_time < %s) OR
                (s.end_time > %s AND s.end_time <= %s)
            )
            AND r.status = 'registered'
        ''', (
            system.current_user_id, session['date'],
            session['end_time'], session['start_time'],
            session['start_time'], session['end_time'],
            session['start_time'], session['end_time']
        ))

        conflicts = cursor.fetchall()
        if conflicts:
            print("\n⏰ Time conflict with existing sessions:")
            for conflict in conflicts:
                print(f"- {conflict['subject']} ({conflict['start_time']}-{conflict['end_time']})")
            choice = input("\nRegister anyway? (yes/no): ").lower()
            while choice not in ['yes', 'no', 'y', 'n']:
                choice = input("Please enter 'yes' or 'no': ").lower()
            if choice in ['no', 'n']:
                return False

        # Register for session
        cursor.execute('''
            INSERT INTO registrations 
            (student_id, session_id, registration_date, status)
            VALUES (%s, %s, %s, %s)
        ''', (
            system.current_user_id,
            session['session_id'],
            datetime.datetime.now().strftime("%Y-%m-%d"),
            "registered"
        ))

        system.connection.commit()
        print(f"\n✅ Successfully registered for session!")
        return True

    except Error as e:
        print(f"\nRegistration failed: {e}")
        system.connection.rollback()
        return False
    finally:
        cursor.close()

""" Displays all active upcoming sessions to the student"""
def student_view_and_register_sessions(system):
    """Show all available sessions with registration option"""
    try:
        cursor = system.connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT s.session_id, s.subject, s.topic, s.date, 
                   s.start_time, s.end_time, s.duration, s.mode,
                   t.name AS tutor_name, t.email AS tutor_email,
                   s.location, s.online_link, s.details
            FROM sessions s
            JOIN tutors t ON s.tutor_id = t.tutor_id
            WHERE s.status = 'active' AND s.date >= CURDATE()
            ORDER BY s.date, s.start_time
        ''')

        sessions = cursor.fetchall()

        if not sessions:
            print("\nNo available sessions at this time.")
            input("\nPress Enter to return to dashboard...")
            return

        print("\n🔍 Available Sessions:")
        for idx, session in enumerate(sessions, 1):
            print(f"\n{idx}. Subject: {session['subject']} - {session['topic']}")
            print(f"   Date: {session['date']} | Time: {session['start_time']}-{session['end_time']}")
            print(f"   Duration: {session['duration']} min | Mode: {session['mode']}")
            print(f"   Tutor: {session['tutor_name']} ({session['tutor_email']})")
            if session['mode'] == 'Online':
                print(f"   Link: {session['online_link']}")
            else:
                print(f"   Location: {session['location']}")
            print(f"   Details: {session['details'] or 'No details available'}")

        while True:
            selection = input("\nEnter session numbers to register (comma separated, 0 to cancel): ").strip()
            if selection == '0':
                break

            selected_indices = []
            for s in selection.split(','):
                s = s.strip()
                if not s.isdigit():
                    print(f"Invalid input '{s}'. Please enter numbers only.")
                    continue
                idx = int(s) - 1
                if 0 <= idx < len(sessions):
                    selected_indices.append(idx)
                else:
                    print(f"Invalid session number {s}. Please enter numbers between 1-{len(sessions)}")

            if not selected_indices:
                continue

            registered_count = 0
            for idx in selected_indices:
                if register_for_session(system, sessions[idx]):
                    registered_count += 1

            if registered_count > 0:
                print(f"\n✅ Successfully registered for {registered_count} session(s)")
            else:
                print("\nNo sessions were registered")

            if input("\nRegister for more sessions? (y/n): ").lower() != 'y':
                break

    except Error as e:
        print(f"\nError viewing sessions: {e}")
        input("\nPress Enter to continue...")
    finally:
        cursor.close()

"""Displays a menu for students to manage their session requests."""
def student_requests_menu(system):
    """Menu for managing session requests"""
    while True:
        print("\n📝 Session Requests Menu")
        print("1. View pending requests and confirm interest")
        print("2. Create new request")
        print("3. Back to Dashboard")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == '1':
            student_view_and_confirm_requests(system)
        elif choice == '2':
            _create_new_request(system)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter 1-3.")

