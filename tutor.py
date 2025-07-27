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
