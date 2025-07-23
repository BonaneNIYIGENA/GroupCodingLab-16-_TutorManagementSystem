import datetime

class TutoringSystem:
    def __init__(self):
        # Data storage
        self.students = {}  # {student_id: {name, email}}
        self.tutors = {}    # {tutor_id: {name, email}}
        self.sessions = {}  # {session_id: session_data}
        self.registrations = []  # [registration_records]
        self.session_requests = {}  # {request_id: request_data}
        self.request_participations = {}  # {request_id: [student_ids]}
        
        # ID counters
        self.student_id_counter = 1
        self.tutor_id_counter = 1
        self.session_id_counter = 1
        self.request_id_counter = 1
        
        # Current user
        self.current_user_id = None
        self.current_user_role = None

    # ID generation methods
    def generate_student_id(self):
        student_id = f"st_{self.student_id_counter:03d}"
        self.student_id_counter += 1
        return student_id

    def generate_tutor_id(self):
        tutor_id = f"ttr_{self.tutor_id_counter:03d}"
        self.tutor_id_counter += 1
        return tutor_id

    def generate_session_id(self):
        session_id = f"sess_{self.session_id_counter:03d}"
        self.session_id_counter += 1
        return session_id

    def generate_request_id(self):
        request_id = f"req_{self.request_id_counter:03d}"
        self.request_id_counter += 1
        return request_id

    # Helper methods
    def get_valid_input(self, prompt, validation_func=None, error_msg="Invalid input!! Please try again"):
        while True:
            user_input = input(prompt).strip()
            if not validation_func or validation_func(user_input):
                return user_input
            print(error_msg)

    # User authentication
    def register_user(self, role):
        print(f"\nRegister as a new {role}")
        name = self.get_valid_input("Your Name: ", lambda x: len(x) > 0)
        email = self.get_valid_input("Your Email: ", lambda x: '@' in x and '.' in x)

        # Check for existing accounts
        existing_ids = []
        for student_id, data in self.students.items():
            if data['email'].lower() == email.lower():
                existing_ids.append((student_id, 'student'))
        for tutor_id, data in self.tutors.items():
            if data['email'].lower() == email.lower():
                existing_ids.append((tutor_id, 'tutor'))

        if existing_ids:
            print("\nAn account with this email already exists:")
            for user_id, user_role in existing_ids:
                print(f"- {user_role.capitalize()} ID: {user_id}")
            
            if role in [r for _, r in existing_ids]:
                print(f"\nYou already have a {role} account. Please login instead.")
                return None

            proceed = input(f"\nDo you want to register as a new {role} with this email? (yes/no): ").lower()
            if proceed != 'yes':
                return None

        # Create new account
        if role == 'student':
            user_id = self.generate_student_id()
            self.students[user_id] = {'name': name, 'email': email}
        else:  # tutor
            user_id = self.generate_tutor_id()
            self.tutors[user_id] = {'name': name, 'email': email}

        print(f"\nRegistration successful! Your {role} ID is: {user_id}")
        return user_id

    def login_user(self):
        print("\nLogin to your account")
        user_id = input("Enter your ID (st_XXX for student, ttr_XXX for tutor): ").strip()

        if user_id.startswith('st_') and user_id in self.students:
            self.current_user_id = user_id
            self.current_user_role = 'student'
            print(f"\nWelcome back, student {self.students[user_id]['name']}!")
            return True
        elif user_id.startswith('ttr_') and user_id in self.tutors:
            self.current_user_id = user_id
            self.current_user_role = 'tutor'
            print(f"\nWelcome back, tutor {self.tutors[user_id]['name']}!")
            return True
        else:
            print("ID not found. Please try again or register as a new user.")
            return False

    # Tutor functions
    def tutor_post_session(self):
        """Tutor menu option 1: Post new session"""
        print("\nPost a New Tutoring Session")
        
        session_data = {
            "tutor_id": self.current_user_id,
            "subject": self.get_valid_input("Subject: ", lambda x: len(x) > 0),
            "topic": self.get_valid_input("Topic: ", lambda x: len(x) > 0),
            "level": self.get_valid_input("Level (Beginner/Intermediate/Advanced): ",lambda x: x.lower() in ['beginner', 'intermediate', 'advanced']).capitalize(),
            "details": input("Details: "),
            "date": self.get_valid_input("Date (YYYY-MM-DD): ", lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-' and datetime.datetime.strptime(x, "%Y-%m-%d") >= datetime.datetime.now()),
            "time": self.get_valid_input("Time (HH:MM): ",lambda x: len(x) == 5 and x[2] == ':'),
            "mode": self.get_valid_input("Mode (Online/In-person): ",lambda x: x.lower() in ['online', 'in-person']).capitalize(),
            "status": "active"
        }
        
        session_id = self.generate_session_id()
        self.sessions[session_id] = session_data
        print(f"\nSession posted successfully! Session ID: {session_id}")

    def tutor_view_requests(self):
        """Tutor menu option 2: View requested sessions"""
        print("\nPending Session Requests from Students:")
        pending_requests = [
            (req_id, req) for req_id, req in self.session_requests.items()
            if req['status'] == 'pending'
        ]
        
        if not pending_requests:
            print("No pending session requests.")
            return
        
        for req_id, req in pending_requests:
            participants = self.request_participations.get(req_id, [])
            print(f"\nRequest ID: {req_id}")
            print(f"Subject: {req['subject']} - {req['topic']}")
            print(f"Level: {req['level']}")
            print(f"Requested by: {len(participants)} students")
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
                    "date": self.get_valid_input("Date (YYYY-MM-DD): ", lambda x: len(x) == 10 and x[4] == '-' and x[7] == '-' and datetime.datetime.strptime(x, "%Y-%m-%d") >= datetime.datetime.now()),
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
                    "request_id": req_id
                }
                
                session_id = self.generate_session_id()
                self.sessions[session_id] = session_data
                self.session_requests[req_id]['status'] = 'fulfilled'
                
                for student_id in participants:
                    self.registrations.append({
                        "student_id": student_id,
                        "session_id": session_id,
                        "registration_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "status": "registered"
                    })
                
                print(f"\nSession created successfully! Session ID: {session_id}")
                print(f"{len(participants)} students have been automatically registered.")

    def tutor_view_scheduled(self):
        """Tutor menu option 3: View scheduled sessions"""
        print("\nYour Scheduled Sessions:")
        tutor_sessions = [
            (sid, session) for sid, session in self.sessions.items()
            if session['tutor_id'] == self.current_user_id and 
            session['status'] == 'active' and
            datetime.datetime.strptime(session['date'], "%Y-%m-%d") >= datetime.datetime.now()
        ]
        
        if not tutor_sessions:
            print("You have no scheduled sessions.")
            return
        
        for session_id, session in tutor_sessions:
            registrations = [
                reg for reg in self.registrations
                if reg['session_id'] == session_id and reg['status'] == 'registered'
            ]
            print(f"\nSession ID: {session_id}")
            print(f"Subject: {session['subject']} - {session['topic']}")
            print(f"Date: {session['date']} | Time: {session['time']}")
            print(f"Mode: {session['mode']}")
            print(f"Students registered: {len(registrations)}")
            if session.get('from_request', False):
                print("This session was created from a student request")

    def tutor_update_session(self):
        """Tutor menu option 4: Update session details"""
        self.tutor_view_scheduled()
        session_id = input("\nEnter the Session ID you want to update (or 'cancel' to go back): ")
        
        if session_id.lower() == 'cancel':
            return
        
        if session_id not in self.sessions:
            print("Invalid Session ID. Please try again.")
            return
        
        session = self.sessions[session_id]
        if session['tutor_id'] != self.current_user_id:
            print("You can only update your own sessions.")
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
        
        if 'updates' not in session:
            session['updates'] = {}
        session['updates'][field] = (session[field], new_value)
        session[field] = new_value
        
        print(f"\n{field.capitalize()} updated successfully!")

    def tutor_flow(self):
        """Tutor menu flow"""
        while True:
            print(f"\nTutor Dashboard - Welcome {self.tutors[self.current_user_id]['name']}!")
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

    # Student functions
    def student_view_available(self):
        """Student menu option 1: View available sessions"""
        print("\nAvailable Tutoring Sessions:")
        available_sessions = [
            (sid, session) for sid, session in self.sessions.items() 
            if session['status'] == 'active' and
            datetime.datetime.strptime(session['date'], "%Y-%m-%d") >= datetime.datetime.now()
        ]
        
        if not available_sessions:
            print("No available sessions at this time.")
            return
        
        for session_id, session in available_sessions:
            tutor = self.tutors.get(session['tutor_id'], {'name': 'Unknown Tutor'})
            print(f"\nSession ID: {session_id}")
            print(f"Subject: {session['subject']} - {session['topic']}")
            print(f"Level: {session['level']}")
            print(f"Date: {session['date']} | Time: {session['time']}")
            print(f"Mode: {session['mode']}")
            print(f"Tutor: {tutor['name']}")
            print(f"Details: {session['details']}")
            if session.get('from_request', False):
                print("⭐ This session was created from a student request")

    def student_request_view(self):
        """Student menu option 2: Request/view requested sessions"""
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
            
            # Check for existing similar request
            existing_request = None
            for req_id, req in self.session_requests.items():
                if (req['subject'].lower() == request_data['subject'].lower() and 
                    req['topic'].lower() == request_data['topic'].lower() and
                    req['level'].lower() == request_data['level'].lower() and
                    req['status'] == 'pending'):
                    existing_request = req_id
                    break
            
            if existing_request:
                if existing_request not in self.request_participations:
                    self.request_participations[existing_request] = []
                self.request_participations[existing_request].append(self.current_user_id)
                print("\nSimilar request found! Added your interest to the existing request.")
                print(f"Now {len(self.request_participations[existing_request])} students are interested in this topic.")
            else:
                request_id = self.generate_request_id()
                self.session_requests[request_id] = request_data
                self.request_participations[request_id] = [self.current_user_id]
                print("\nYour session request has been submitted! Tutors will be notified.")
        
        elif sub_choice == '2':
            print("\nRequested Sessions (Not yet scheduled):")
            pending_requests = [
                (req_id, req) for req_id, req in self.session_requests.items()
                if req['status'] == 'pending'
            ]
            
            if not pending_requests:
                print("No requested sessions at this time.")
                return
            
            for req_id, req in pending_requests:
                participants = self.request_participations.get(req_id, [])
                print(f"\nRequest ID: {req_id}")
                print(f"Subject: {req['subject']} - {req['topic']}")
                print(f"Level: {req['level']}")
                print(f"Requested by: {len(participants)} students")
                print(f"Details: {req['details']}")
                
                if self.current_user_id in participants:
                    print("✅ You have confirmed participation in this request")
                else:
                    confirm = input("Would you like to confirm participation in this request? (yes/no): ").lower()
                    if confirm == 'yes':
                        participants.append(self.current_user_id)
                        print("Thank you for confirming your interest!")

    def student_register(self):
        """Student menu option 3: Session registration"""
        self.student_view_available()
        session_id = input("\nEnter the Session ID you want to register for (or 'cancel' to go back): ")
        
        if session_id.lower() == 'cancel':
            return
        
        if session_id not in self.sessions:
            print("Invalid Session ID. Please try again.")
            return
        
        # Check if already registered
        if any(
            reg['student_id'] == self.current_user_id and reg['session_id'] == session_id
            for reg in self.registrations
        ):
            print("You are already registered for this session.")
            return
        
        # Add registration
        self.registrations.append({
            "student_id": self.current_user_id,
            "session_id": session_id,
            "registration_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": "registered"
        })
        
        print("Registration successful!")

    def student_view_scheduled(self):
        """Student menu option 4: View all scheduled sessions (registered and confirmed requests)"""
        print("\nYour Scheduled Sessions:")
        
        # Get registered sessions
        registered_sessions = []
        for reg in self.registrations:
            if reg['student_id'] == self.current_user_id and reg['status'] == 'registered':
                session = self.sessions.get(reg['session_id'])
                if session and session['status'] == 'active':
                    registered_sessions.append((
                        reg['session_id'],
                        session,
                        'registered',
                        reg['registration_date']
                    ))
        
        # Get confirmed requests that became sessions
        confirmed_requests = []
        for req_id, req in self.session_requests.items():
            if req['status'] == 'fulfilled' and self.current_user_id in self.request_participations.get(req_id, []):
                session = next(
                    (s for s in self.sessions.values() 
                     if s.get('request_id') == req_id and s['status'] == 'active'),
                    None
                )
                if session:
                    confirmed_requests.append((
                        session['request_id'],
                        session,
                        'from_request',
                        req['request_date']
                    ))
        
        if not registered_sessions and not confirmed_requests:
            print("You have no scheduled sessions.")
            return
        
        # Display registered sessions
        if registered_sessions:
            print("\nRegistered Sessions:")
            for session_id, session, _, reg_date in registered_sessions:
                tutor = self.tutors.get(session['tutor_id'], {'name': 'Unknown Tutor'})
                print(f"\nSession ID: {session_id}")
                print(f"Subject: {session['subject']} - {session['topic']}")
                print(f"Level: {session['level']}")
                print(f"Date: {session['date']} | Time: {session['time']}")
                print(f"Mode: {session['mode']}")
                print(f"Tutor: {tutor['name']}")
                print(f"Details: {session['details']}")
                print(f"Registration Date: {reg_date}")
                if session.get('updates'):
                    print("\nUpdates:")
                    for field, (old_val, new_val) in session['updates'].items():
                        print(f"- {field.capitalize()} changed from '{old_val}' to '{new_val}'")
        
        # Display confirmed requests
        if confirmed_requests:
            print("\nConfirmed Request Sessions:")
            for req_id, session, _, req_date in confirmed_requests:
                tutor = self.tutors.get(session['tutor_id'], {'name': 'Unknown Tutor'})
                print(f"\nRequest ID: {req_id}")
                print(f"Session ID: {next(k for k,v in self.sessions.items() if v == session)}")
                print(f"Subject: {session['subject']} - {session['topic']}")
                print(f"Level: {session['level']}")
                print(f"Date: {session['date']} | Time: {session['time']}")
                print(f"Mode: {session['mode']}")
                print(f"Tutor: {tutor['name']}")
                print(f"Details: {session['details']}")
                print(f"Original Request Date: {req_date}")
                print("⭐ This session was created from your request")
                if session.get('updates'):
                    print("\nUpdates:")
                    for field, (old_val, new_val) in session['updates'].items():
                        print(f"- {field.capitalize()} changed from '{old_val}' to '{new_val}'")

    def student_flow(self):
        """Student menu flow"""
        while True:
            print(f"\nStudent Dashboard - Welcome {self.students[self.current_user_id]['name']}!")
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

    # Main system flow
    def run(self):
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
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    system = TutoringSystem()
    system.run()