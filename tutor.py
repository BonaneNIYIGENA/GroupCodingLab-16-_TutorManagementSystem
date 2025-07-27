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
