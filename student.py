import datetime
from getpass import getpass
from mysql.connector import Error

"""
   Function that allows displays the student dashboard interface
 """
def student_flow(system):
    """Student dashboard with direct session viewing/registration"""
    while True:
        print(f"\n Student Dashboard - Welcome {system.current_user_name}!")
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
