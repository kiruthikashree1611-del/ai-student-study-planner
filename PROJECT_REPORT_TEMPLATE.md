# AI-Based Student Study Planner
## Project Report Template

### Title
AI-Based Student Study Planner

### Abstract
The Student Study Planner is a Python-based application designed to help students organize their study activities. Users can add subjects, exam dates, difficulty levels, and preparation levels. The application uses a rule-based recommendation algorithm to prioritize subjects and generate study tasks. It stores information using SQLite and provides a dashboard to track task completion.

### 1. Introduction
Students often need to manage several subjects and deadlines at the same time. A structured planner can help them arrange study sessions and track progress.

### 2. Problem Statement
Manual planning can be difficult to update and may not make it easy to compare subject urgency, difficulty, and preparation level.

### 3. Objectives
- Maintain a list of subjects and exam dates.
- Recommend study priorities using transparent rules.
- Generate study tasks for a selected period.
- Track completed and pending tasks.
- Display overall progress.

### 4. Proposed System
The system uses Streamlit for the user interface, Python for application logic, and SQLite for persistent storage. A rule-based score ranks subjects using exam urgency, difficulty, and preparation level.

### 5. Software Requirements
- Python 3.9 or later
- Streamlit
- SQLite
- Web browser
- VS Code or PyCharm (recommended)

### 6. Modules
1. Subject Management
2. Priority Recommendation
3. Study Plan Generation
4. Task Tracking
5. Dashboard and Progress Report

### 7. Algorithm
Priority Score = 0.5 × Urgency + 2 × Difficulty + 0.8 × (10 − Preparation)

Higher scores indicate that a subject may deserve more attention. Urgency increases as the exam date approaches.

### 8. Database Design
**subjects:** id, name, exam_date, difficulty, preparation, weekly_hours  
**tasks:** id, subject_id, title, task_date, duration, completed

### 9. Testing
Record the actual outcome after testing each case:
- Add a subject with valid details.
- Try adding a duplicate subject name.
- Generate a seven-day study plan.
- Mark a task as complete.
- Verify dashboard completion percentage.
- Delete a subject and verify its tasks are removed.

### 10. Limitations
The current version uses rule-based recommendations and does not train a machine-learning model. The plan is a suggested schedule and should be adjusted to each student's actual timetable.

### 11. Future Enhancements
- Calendar and reminder integration
- CSV/PDF export
- Machine-learning recommendations based on study history
- Optional chatbot for study tips

### 12. Conclusion
The application demonstrates how Python, a simple web interface, a database, and a priority algorithm can be combined to create a useful student planning tool.
