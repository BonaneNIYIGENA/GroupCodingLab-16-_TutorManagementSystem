# GroupCodingLab-16-_TutorManagementSystem
**command-line tutoring management system** built with **Python 3** and **MySQL**.

This is a command-line tutoring management application built using Python and MySQL. The system provides separate dashboards for tutors and students, enabling them to manage tutoring sessions, requests, and schedules in an organized and efficient way.

It provides separate dashboards for **students** and **tutors**, supporting session registrations, requests, and scheduling.

---

## **Features**

### **Student Dashboard**

A menu-based CLI where students can:

    View and register for available sessions.

    Manage session requests.

    View or cancel their scheduled sessions.

    Logout.

View and Register for Sessions:

    Students can view all active sessions with full details (subject, date, tutor name, time, mode, and location/link).

    Collision check: The system detects time conflicts with the student’s existing sessions and alerts them before registering.

Session Requests:

    Students can view all pending requests and confirm participation in a request.

    Students can create new session requests (subject, topic, level, details).

    If a similar request already exists, the student is added to that request instead of creating a duplicate.

Session Schedule:

    Students can view all their upcoming registered sessions and sessions created from confirmed requests.

    Sessions are displayed with details like date, time, duration, tutor name, and mode.

Cancel a Session:

    Students can cancel their registrations with a reason, which is stored in the cancellations log.

### **Tutor Dashboard**

A simple menu-based CLI where tutors can:

    Post new tutoring sessions.

    View and respond to student requests.

    Update or manage scheduled sessions.

    Logout.

Post a New Session:

    Tutors can create a session by providing subject, topic, level, details, date, start time, duration, and mode (Online/In-person).

    Time conflict detection: The system checks existing sessions for overlapping time slots and prevents conflicts.

    Location or online link is required depending on session mode.

View Student Requests:

    Tutors can view pending requests created by students (with the number of students interested).

    Tutors can confirm and convert a request into a scheduled session by filling in session details.

    Students who joined the request are automatically registered when a tutor fulfills the request.

Update Scheduled Sessions:

    Tutors can view a list of all active sessions they created.

    Sessions can be updated (subject, time, mode, details, etc.) with all changes recorded in a session_updates log.

View Scheduled Sessions:

    A simple read-only list of all upcoming sessions, with details like date, time, mode, and registered students.

### **Database**

The app uses MySQL for persistent storage with tables such as:

    sessions – All tutoring sessions.

    registrations – Students’ session registrations.

    session_requests – Requests created by students.

    request_participations – Students joining existing requests.

    cancellations – Logs of cancelled sessions.

    session_updates – Logs of changes made to sessions.

Transactions and Rollbacks:

    Critical operations (e.g., creating sessions, cancelling, or confirming requests) are wrapped in transactions for data integrity.

Time and Date Validations:

    The app prevents scheduling sessions in the past and ensures correct time formats (HH:MM), date formats (YYYY-MM-DD), and duration.

---

## **Tech Stack**

- **Language:** Python
- **Database:** MySQL
- **Library:** `mysql-connector-python`, `datetime`, `hashlib`,`re`
- **Interface:** CLI

