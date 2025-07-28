# Tutoring Management System (TMS)

![Python](https://img.shields.io/badge/Python-blue)
![MySQL](https://img.shields.io/badge/MySQL-orange)

## Project Description

Tutoring Management System is Python-based, terminal-driven application to connect students with qualified tutors for personalized learning. This system aims to simplify the process of students to find academic support across various subjects and empower tutors to efficiently connect with students seeking their specific expertise. It focuses on facilitating seamless educational connections for knowledge sharing.

---

## ✨ Features

### 👩‍🎓 Student Module

* ✅ Register and log in as a student
* 📚 View available sessions 
* ✍ Request and view requested sessions
* 📅 Book and cancel session registrations
* ⏰ Prevent double-booking with time conflict detection

### 👨‍🏫 Tutor Module

* ✅ Register and log in as a tutor
* 📅 Create, view, and manage tutoring sessions
* 📩 View and fulfill student-initiated session requests
* ✏ Update or cancel scheduled sessions

### 🔐 System & Backend

* Secure login via password hashing
* MySQL-based persistent storage system that os cloud based meaning also auto-syncing of data
* Modular design for maintainability (Modules helping in maintaining the system)
* Automatic database and tables creation (if not present)

---

##  Project Structure

```
GroupCodingLab-16-_TutorManagementSystem/
├── main.py           # Main application loop and shared utilities
├── student.py        # Student interface and logic
├── tutor.py          # Tutor interface and logic
└── README.md         # Project documentation
```

---

##  Installation & Setup

###  Requirements

* Python
* MySQL Server
* `mysql-connector-python` as a package required

###  Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/BonaneNIYIGENA/GroupCodingLab-16-_TutorManagementSystem.git
   cd GroupCodingLab-16-_TutorManagementSystem/
   ```

2. **Install dependencies:**

   ```bash
   pip install mysql-connector-python
   ``` 
3. **Run the application:**

   ```bash
   python main.py
   or
   python3 main.py
   ```

4. Database creation and syncing
    ```bash
   Database called "tms" is created and connects
   or
   database exists it immediately connects
   ```
##  Usage Guide

### Student Flow

* Register or log in
* View available sessions
* Register or cancel session bookings
* Submit topic requests if needed

### Tutor Flow

* Register or log in
* Create tutoring sessions
* View/approve topic requests
* Edit or delete sessions as needed

---

##  Key Components

###  Core system functions

* `TutoringSystem` — Main orchestrator (in `main.py`)
* `student_flow()` — Student menu logic
* `tutor_flow()` — Tutor menu logic
* `register_user()` — Creates new student/tutor accounts
* `login_user()` — Authenticates users
* `register_for_session()` — Registers students into a session
* `tutor_post_session()` — Lets tutors post sessions
* `handle_requests()` — Manages topic requests

---

## Authors and creators (African Leadership University Year1 students)
- Bonane NIYIGENA
- Rhoda Nicole Umutesi
- Fabrice Mbarushimana
- Maxime Hirwa  Lilian
- Muhammed Awwal Achuja
- Nyiramanzi Igihozo