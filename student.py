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
