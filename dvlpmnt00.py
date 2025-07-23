import datetime

class TutoringSystem:
    def __init__(self):
        # Data Storage Structures
        self.users = {}
        self.sessions = {}
        self.registrations = []
        
        # ID counters
        self.user_id_counter = 1
        self.session_id_counter = 1
        self.registration_id_counter = 1
        
        # Current user tracking
        self.current_user = None
        self.current_role = None

    def _generate_id(self, id_type):
        """Generate unique IDs based on type"""
        if id_type == 'user':
            id_num = self.user_id_counter
            self.user_id_counter += 1
            return f"user_{id_num:03d}"
        elif id_type == 'session':
            id_num = self.session_id_counter
            self.session_id_counter += 1
            return f"session_{id_num:03d}"
        elif id_type == 'registration':
            id_num = self.registration_id_counter
            self.registration_id_counter += 1
            return f"reg_{id_num:03d}"
        return ""

    def _get_valid_input(self, prompt, validation_func=None, error_msg="Invalid input. Please try again."):
        """Helper method to get validated user input"""
        while True:
            user_input = input(prompt).strip()
            if not validation_func or validation_func(user_input):
                return user_input
            print(error_msg)

    def _create_user(self):
        """Create a new user record"""
        print("\nPlease enter your details:")
        name = self._get_valid_input("Your Name: ", lambda x: len(x) > 0)
        email = self._get_valid_input("Your Email: ", lambda x: '@' in x and '.' in x)
        
        user_id = self._generate_id('user')
        self.users[user_id] = {
            "role": self.current_role,
            "name": name,
            "email": email
        }
        self.current_user = user_id
        return user_id

    def _post_new_session(self):
        """Tutor posts a new session"""
        print("\nPost a New Tutoring Session")
        
        session_data = {
            "tutor_id": self.current_user,
            "subject": self._get_valid_input("Subject: ", lambda x: len(x) > 0),
            "topic": self._get_valid_input("Topic: ", lambda x: len(x) > 0),
            "level": self._get_valid_input(
                "Level (Beginner/Intermediate/Advanced): ",
                lambda x: x.lower() in ['beginner', 'intermediate', 'advanced']
            ).capitalize(),
            "details": input("Details: "),
            "date": self._get_valid_input(
                "Date (YYYY-MM-DD): ",
                lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-'
            ),
            "time": self._get_valid_input(
                "Time (HH:MM): ",
                lambda x: len(x) == 5 and x[2] == ':'
            ),
            "mode": self._get_valid_input(
                "Mode (Online/In-person): ",
                lambda x: x.lower() in ['online', 'in-person']
            ).capitalize(),
            "status": "active"
        }
        
        session_id = self._generate_id('session')
        self.sessions[session_id] = session_data
        
        print(f"\nSession posted successfully! Session ID: {session_id}")

    def _view_available_sessions(self):
        """Display all available sessions"""
        print("\nAvailable Tutoring Sessions:")
        available_sessions = [
            (sid, session) for sid, session in self.sessions.items() 
            if session['status'] == 'active'
        ]
        
        if not available_sessions:
            print("No available sessions at this time.")
            return
        
        for session_id, session in available_sessions:
            tutor = self.users.get(session['tutor_id'], {'name': 'Unknown Tutor'})
            print(f"\nSession ID: {session_id}")
            print(f"Subject: {session['subject']} - {session['topic']}")
            print(f"Level: {session['level']}")
            print(f"Date: {session['date']} | Time: {session['time']}")
            print(f"Mode: {session['mode']}")
            print(f"Tutor: {tutor['name']}")
            print(f"Details: {session['details']}")

    def _register_for_session(self):
        """Student registers for a session"""
        self._view_available_sessions()
        session_id = input("\nEnter the Session ID you want to register for (or 'cancel' to go back): ")
        
        if session_id.lower() == 'cancel':
            return
        
        if session_id not in self.sessions:
            print("Invalid Session ID. Please try again.")
            return
        
        # Check if already registered
        if any(
            reg['student_id'] == self.current_user and reg['session_id'] == session_id
            for reg in self.registrations
        ):
            print("You are already registered for this session.")
            return
        
        # Add registration
        self.registrations.append({
            "registration_id": self._generate_id('registration'),
            "student_id": self.current_user,
            "session_id": session_id,
            "registration_date": datetime.datetime.now().strftime("%Y-%m-%d")
        })
        
        print("Registration successful!")

    def _view_student_scheduled_sessions(self):
        """Display sessions a student has registered for"""
        print("\nYour Scheduled Sessions:")
        student_sessions = [
            (reg['session_id'], self.sessions[reg['session_id']])
            for reg in self.registrations
            if reg['student_id'] == self.current_user and reg['session_id'] in self.sessions
        ]
        
        if not student_sessions:
            print("You have no scheduled sessions.")
            return
        
        for session_id, session in student_sessions:
            tutor = self.users.get(session['tutor_id'], {'name': 'Unknown Tutor'})
            print(f"\nSession ID: {session_id}")
            print(f"Subject: {session['subject']} - {session['topic']}")
            print(f"Date: {session['date']} | Time: {session['time']}")
            print(f"Tutor: {tutor['name']} | Mode: {session['mode']}")

    def _view_tutor_scheduled_sessions(self):
        """Display sessions a tutor has created"""
        print("\nYour Scheduled Sessions:")
        tutor_sessions = [
            (sid, session) for sid, session in self.sessions.items()
            if session['tutor_id'] == self.current_user
        ]
        
        if not tutor_sessions:
            print("You have no scheduled sessions.")
            return
        
        for session_id, session in tutor_sessions:
            registrations = [
                reg for reg in self.registrations
                if reg['session_id'] == session_id
            ]
            print(f"\nSession ID: {session_id}")
            print(f"Subject: {session['subject']} - {session['topic']}")
            print(f"Date: {session['date']} | Time: {session['time']}")
            print(f"Students registered: {len(registrations)} | Mode: {session['mode']}")

    def _view_registered_students(self):
        """Display students registered for tutor's sessions"""
        print("\nStudents Registered for Your Sessions:")
        tutor_sessions = [
            sid for sid, session in self.sessions.items()
            if session['tutor_id'] == self.current_user
        ]
        
        if not tutor_sessions:
            print("You have no sessions with registered students.")
            return
        
        for session_id in tutor_sessions:
            session = self.sessions[session_id]
            session_registrations = [
                reg for reg in self.registrations
                if reg['session_id'] == session_id
            ]
            
            if session_registrations:
                print(f"\nSession: {session['subject']} - {session['topic']}")
                print(f"Date: {session['date']} | Time: {session['time']}")
                print("Registered Students:")
                
                for reg in session_registrations:
                    student = self.users.get(reg['student_id'], {'name': 'Unknown Student'})
                    print(f"- {student['name']} (Student ID: {reg['student_id']})")

    def _student_flow(self):
        """Student user flow"""
        print("\nStudent Mode Selected")
        self.current_role = "student"
        self._create_user()
        
        while True:
            print(f"\nStudent Dashboard - Welcome {self.users[self.current_user]['name']}!")
            print("1. View available sessions")
            print("2. Register for a session")
            print("3. View my scheduled sessions")
            print("4. Exit")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                self._view_available_sessions()
            elif choice == '2':
                self._register_for_session()
            elif choice == '3':
                self._view_student_scheduled_sessions()
            elif choice == '4':
                print("Returning to main menu.")
                break
            else:
                print("Invalid choice. Please try again.")

    def _tutor_flow(self):
        """Tutor user flow"""
        print("\nTutor Mode Selected")
        self.current_role = "tutor"
        self._create_user()
        
        while True:
            print(f"\nTutor Dashboard - Welcome {self.users[self.current_user]['name']}!")
            print("1. Post new session")
            print("2. View my scheduled sessions")
            print("3. View registered students")
            print("4. Exit")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                self._post_new_session()
            elif choice == '2':
                self._view_tutor_scheduled_sessions()
            elif choice == '3':
                self._view_registered_students()
            elif choice == '4':
                print("Returning to main menu.")
                break
            else:
                print("Invalid choice. Please try again.")

    def run(self):
        """Main application loop"""
        print("\nWelcome to Tutoring Management System!")
        
        while True:
            print("\nMain Menu")
            print("1. Enter as Student")
            print("2. Enter as Tutor")
            print("3. Exit System")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                self._student_flow()
            elif choice == '2':
                self._tutor_flow()
            elif choice == '3':
                print("\nThank you for using the Tutoring Management System. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    system = TutoringSystem()
    system.run()