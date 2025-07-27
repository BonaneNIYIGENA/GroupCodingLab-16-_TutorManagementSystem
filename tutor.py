import datetime
from mysql.connector import Error

def tutor_flow(system):
    """Simplified tutor main dashboard"""
    while True:
        print(f"\nTutor Dashboard - Welcome {system.current_user_name}!")
        print("1. Manage Sessions")
        print("2. View Scheduled Sessions")
        print("3. Logout")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            tutor_manage_sessions(system)
        elif choice == '2':
            tutor_view_scheduled_simple(system)
        elif choice == '3':
            print("Logging out...")
            system.current_user_id = None
            system.current_user_role = None
            system.current_user_name = None
            break
        else:
            print("Invalid choice. Please try again.")

def tutor_post_session(system):
    """Post session with time conflict check"""
    print("\nPost a New Tutoring Session")

    session_data = {
        "tutor_id": system.current_user_id,
        "subject": system.get_valid_input("Subject: ", lambda x: len(x) > 0),
        "topic": system.get_valid_input("Topic: ", lambda x: len(x) > 0),
        "level": system.get_valid_input(
            "Level (Beginner/Intermediate/Advanced): ",
            lambda x: x.lower() in ['beginner', 'intermediate', 'advanced']
        ).capitalize(),
        "details": input("Details: "),
        "date": system.get_valid_input(
            "Date (YYYY-MM-DD): ",
            lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-' and
                      datetime.datetime.strptime(x, "%Y-%m-%d") >= datetime.datetime.now()
        )
    }

    # Time entry with immediate conflict check
    while True:
        session_data['start_time'] = system.get_valid_input("Start Time (HH:MM): ", lambda x: len(x) == 5 and x[2] == ':')
        session_data['duration'] = int(system.get_valid_input("Duration (minutes): ", lambda x: x.isdigit() and int(x) > 0))
        session_data['end_time'] = system.calculate_end_time(session_data['start_time'], session_data['duration'])

        # Check for time conflicts
        try:
            cursor = system.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT session_id, subject, start_time, end_time FROM sessions WHERE tutor_id = %s AND date = %s AND status = 'active'
            ''', (system.current_user_id, session_data['date']))

            conflict_found = False
            for existing in cursor.fetchall():
                existing_start = datetime.datetime.strptime(str(existing['start_time']), "%H:%M:%S").time()
                existing_end = datetime.datetime.strptime(str(existing['end_time']), "%H:%M:%S").time()
                new_start = datetime.datetime.strptime(session_data['start_time'], "%H:%M").time()
                new_end = datetime.datetime.strptime(session_data['end_time'], "%H:%M").time()

                if (new_start < existing_end and new_end > existing_start):
                    print(f"\n⏰ Time conflict with existing session:")
                    print(f"Session ID: {existing['session_id']}")
                    print(f"Subject: {existing['subject']}")
                    print(f"Time: {existing['start_time']}-{existing['end_time']}")
                    conflict_found = True
                    break

            if conflict_found:
                print("\nThis session overlaps with an existing session.")
                choice = input(
                    "Would you like to: \n1. Enter a new time\n2. Cancel this session\nEnter choice (1/2): ")
                if choice == '1':
                    continue  # Just re-prompt for time
                else:
                    print("Session posting cancelled.")
                    return
            else:
                break  # No conflicts, proceed

        except Error as e:
            print(f"Error checking for time conflicts: {e}")
            return
        finally:
            cursor.close()

    # Get remaining details after time is confirmed
    session_data['mode'] = system.get_valid_input("Mode (Online/In-person): ", lambda x: x.lower() in ['online', 'in-person']).capitalize()

    # Add location/link based on mode
    if session_data['mode'] == 'In-person':
        session_data['location'] = system.get_valid_input("Location: ", lambda x: len(x) > 0)
        session_data['online_link'] = None
    else:
        session_data['online_link'] = system.get_valid_input("Online meeting link: ", lambda x: len(x) > 0)
        session_data['location'] = None

    # Post the session
    try:
        cursor = system.connection.cursor()
        session_id = system.generate_id('session')

        cursor.execute('''
            INSERT INTO sessions (
                session_id, tutor_id, subject, topic, level, details, date, start_time, duration, end_time, mode, status, location, online_link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (session_id, session_data['tutor_id'], session_data['subject'], session_data['topic'], session_data['level'], session_data['details'], session_data['date'], session_data['start_time'], session_data['duration'], session_data['end_time'], session_data['mode'], 'active', session_data['location'], session_data['online_link']))

        system.connection.commit()
        print(f"\nSession posted successfully! Session ID: {session_id}")

    except Error as e:
        print(f"\nError posting session: {e}")
        system.connection.rollback()
    finally:
        cursor.close()
