# AI-Based Student Study Planner

A beginner-friendly Python project that helps students organize subjects, generate a study plan, and track task completion.

## Features
- Add and delete subjects
- Record exam date, difficulty, preparation level, and target weekly hours
- Generate a study plan using a transparent rule-based priority score
- Mark tasks completed
- View dashboard and completion percentage
- Store data locally in SQLite

## Requirements
- Python 3.9 or later recommended
- Streamlit

## Setup
1. Extract this folder.
2. Open a terminal inside the project folder.
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Run:
   `python -m streamlit run app.py`
5. Your browser should open the application.

## Database
The `study_planner.db` file is created automatically on first run.

## Algorithm
Priority Score = 0.5 × Urgency + 2 × Difficulty + 0.8 × (10 − Preparation)

Urgency is assigned based on how close the exam date is. This is a rule-based recommendation system, not a trained machine-learning model.

## Future enhancements
- Weekly calendar view
- Reminder notifications
- Export plan to CSV/PDF
- Optional integration with a language model API
