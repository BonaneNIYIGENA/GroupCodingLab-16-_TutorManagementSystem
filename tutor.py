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

def tutor_view_requests(system):
    """Tutor views pending session requests with improved confirmation flow"""
    print("\nPending Session Requests from Students:")

    try:
        cursor = system.connection.cursor(dictionary=True)

        # Get pending requests with participant counts
        cursor.execute('''
            SELECT sr.request_id, sr.subject, sr.topic, sr.level, sr.details, COUNT(rp.student_id) AS participant_count FROM session_requests sr LEFT JOIN request_participations rp ON sr.request_id = rp.request_id WHERE sr.status = 'pending' GROUP BY sr.request_id, sr.subject, sr.topic, sr.level, sr.details
        ''')

        pending_requests = cursor.fetchall()

        if not pending_requests:
            print("No pending session requests.")
            return

        for req in pending_requests:
            print(f"\n📌 Pending Session Request")
            print(f"Request ID: {req['request_id']}")
            print(f"Subject: {req['subject']} - {req['topic']}")
            print(f"Level: {req['level']}")
            print(f"Requested by: {req['participant_count']} students")
            print(f"Details: {req['details']}")

            confirm = input("\nWould you like to confirm this session? (yes/no): ").lower()
            if confirm == 'yes':
                print("\nPlease provide the session details below:")

                session_data = {
                    "tutor_id": system.current_user_id,
                    "subject": req['subject'],
                    "topic": req['topic'],
                    "level": req['level'],
                    "details": req['details'],
                    "date": system.get_valid_input("Date (YYYY-MM-DD): ", lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-' and datetime.datetime.strptime(x, "%Y-%m-%d") >= datetime.datetime.now()),
                    "start_time": system.get_valid_input("Start Time (HH:MM): ", lambda x: len(x) == 5 and x[2] == ':'),
                    "duration": int(system.get_valid_input("Duration (minutes): ", lambda x: x.isdigit() and int(x) > 0)),
                    "mode": system.get_valid_input("Mode (1. Online / 2. In-person): ", lambda x: x in ['1', '2'])
                }

                # Convert mode selection
                session_data['mode'] = 'Online' if session_data['mode'] == '1' else 'In-person'

                # Calculate end time
                session_data['end_time'] = system.calculate_end_time(session_data['start_time'], session_data['duration'])

                # Get mode-specific details
                if session_data['mode'] == 'In-person':
                    session_data['location'] = system.get_valid_input("Location: ", lambda x: len(x) > 0)
                    session_data['online_link'] = None
                else:
                    session_data['online_link'] = system.get_valid_input("Online meeting link: ", lambda x: len(x) > 0)
                    session_data['location'] = None

                # Final confirmation
                final_confirm = input("\nConfirm session? (yes/no): ").lower()
                if final_confirm != 'yes':
                    print("Session confirmation cancelled.")
                    continue

                try:
                    # Start transaction
                    cursor.execute("START TRANSACTION")

                    # Create the session
                    session_id = system.generate_id('session')
                    cursor.execute('''
                        INSERT INTO sessions (session_id, tutor_id, subject, topic, level, details, date, start_time, duration, end_time, mode, status, from_request, request_id, location, online_link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (session_id, session_data['tutor_id'], session_data['subject'], session_data['topic'], session_data['level'], session_data['details'], session_data['date'], session_data['start_time'], session_data['duration'], session_data['end_time'], session_data['mode'], 'active', True, req['request_id'], session_data['location'], session_data['online_link']))

                    # Update request status
                    cursor.execute('''
                        UPDATE session_requests SET status = 'fulfilled' WHERE request_id = %s
                    ''', (req['request_id'],))

                    # Register all participating students
                    cursor.execute('''
                        SELECT student_id FROM request_participations WHERE request_id = %s
                    ''', (req['request_id'],))
                    participants = cursor.fetchall()

                    for participant in participants:
                        cursor.execute('''
                            INSERT INTO registrations (student_id, session_id, registration_date, status) VALUES (%s, %s, %s, %s)
                        ''', (
                            participant['student_id'], session_id,
                            datetime.datetime.now().strftime("%Y-%m-%d"), "registered"
                        ))

                    system.connection.commit()
                    print(f"\n✅ Session created successfully! Session ID: {session_id}")
                    print(f"{len(participants)} students have been automatically registered.")

                except Error as e:
                    system.connection.rollback()
                    print(f"\nError creating session from request: {e}")
                    if "unique_session_time" in str(e):
                        print("A session already exists at this date and time. Please choose a different time.")

    except Error as e:
        print(f"\nError viewing requests: {e}")
    finally:
        cursor.close()
