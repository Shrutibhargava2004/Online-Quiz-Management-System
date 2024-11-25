# Web-Based Quiz Management System

The **Web-Based Quiz Management System** is a robust and user-friendly platform designed for creating, managing, and participating in quizzes online. It streamlines assessments, performance analysis, and user management with an intuitive interface, making it ideal for educational institutions and professional training environments.

---

## Key Features

### 1. **Role-Based Access:**
   - **Admin:**
     - Registers Teachers and Students.
     - Monitors quiz activities and system usage.
   - **Teacher:**
     - Creates, manages, and monitors quizzes.
     - Analyzes detailed performance reports of students.
   - **Student:**
     - Participates in quizzes using batch enrollment or a unique code.
     - Receives instant results upon quiz submission.

### 2. **Quiz Management:**
   - Flexible quiz creation with support for multiple-choice questions.
   - Time-bound quizzes with automatic response cut-off.
   - Unique 6-digit codes for quick quiz access.

### 3. **Performance Analysis:**
   - Teachers view individual and batch performance metrics.
   - Students access their quiz scores and feedback immediately.

### 4. **Responsive Design:**
   - Optimized for desktops, tablets, and mobile devices.

### 5. **Secure Database Management:**
   - Ensures accurate storage of user details, quiz data, and results.

---

## Technology Stack

- **Frontend:** HTML, CSS, Bootstrap for responsive UI design.
- **Backend:** Flask (Python) for server-side logic and API handling.
- **Database:** MySQL for efficient and secure data management.

---

## Installation Guide

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/quiz-management-system.git
2. Set Up Environment:
   Install Python (3.8+ recommended).
   Install dependencies
3. Configure Database:
   Import the provided MySQL schema.
   Update database credentials in the application configuration.
4. Run the Application:
   ```bash
   pyhton app.py
5. Access the Application:
   Open your browser and navigate to http://127.0.0.1:5000.

## Usage Workflow
- Admin: Registers users, monitors system activities, and provides credentials.
- Teacher: Creates quizzes, sets parameters, and reviews results.
- Student: Logs in, joins quizzes, and views scores.
