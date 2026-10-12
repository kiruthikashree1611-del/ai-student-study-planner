import sqlite3
from datetime import date, timedelta
import streamlit as st

DB_PATH = "study_planner.db"

st.set_page_config(page_title="AI Study Planner", page_icon="📚", layout="wide")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                exam_date TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                preparation INTEGER NOT NULL,
                weekly_hours REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                task_date TEXT NOT NULL,
                duration REAL NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        """)

def fetch_subjects():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name, exam_date, difficulty, preparation, weekly_hours
            FROM subjects ORDER BY exam_date
        """).fetchall()

def fetch_tasks():
    with get_connection() as conn:
        return conn.execute("""
            SELECT tasks.id, subjects.name, tasks.title, tasks.task_date,
                   tasks.duration, tasks.completed, tasks.subject_id
            FROM tasks JOIN subjects ON subjects.id = tasks.subject_id
            ORDER BY tasks.task_date, tasks.id
        """).fetchall()

def priority_score(exam_date, difficulty, preparation):
    days_left = max((date.fromisoformat(exam_date) - date.today()).days, 0)
    urgency = 10 if days_left <= 3 else 8 if days_left <= 7 else 6 if days_left <= 14 else 3
    return urgency * 0.5 + difficulty * 2 + (10 - preparation) * 0.8

def generate_plan(subjects, days, hours_per_day):
    # Rule-based recommendations: urgency, difficulty, and preparation level.
    weighted = []
    for subject in subjects:
        sid, name, exam_date, difficulty, preparation, weekly_hours = subject
        score = priority_score(exam_date, difficulty, preparation)
        weighted.append((sid, name, score, difficulty, preparation, exam_date))
    weighted.sort(key=lambda x: x[2], reverse=True)

    if not weighted:
        return []

    total_slots = max(1, int(days * hours_per_day / 1.0))
    # Give at least one session to each subject when possible, then distribute remaining slots by priority.
    slots = {item[0]: 0 for item in weighted}
    for item in weighted[:total_slots]:
        slots[item[0]] += 1
    remaining = total_slots - sum(slots.values())
    for i in range(remaining):
        slots[weighted[i % len(weighted)][0]] += 1

    plan = []
    start = date.today()
    ordered = []
    for item in weighted:
        ordered.extend([item] * slots[item[0]])

    # Interleave subjects by score-ranked order so the plan is easy to follow.
    for i, item in enumerate(ordered):
        day_num = i % days
        task_date = start + timedelta(days=day_num)
        sid, name, score, difficulty, preparation, exam_date = item
        plan.append((sid, name, f"Study {name} — Session {i + 1}", task_date.isoformat(), 1.0))
    return plan

init_db()

st.title("📚 AI-Based Student Study Planner")
st.caption("Plan smarter, track your progress, and prepare for exams with personalized study recommendations.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose a section", ["Dashboard", "Manage Subjects", "Generate Study Plan", "My Tasks", "About Project"])
    st.divider()
    st.caption("Recommendations are generated using transparent rules based on exam urgency, difficulty, and preparation level.")

subjects = fetch_subjects()
tasks = fetch_tasks()

if page == "Dashboard":
    st.subheader("Your study overview")
    total_subjects = len(subjects)
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task[5] == 1)
    pending_tasks = total_tasks - completed_tasks
    progress = (completed_tasks / total_tasks * 100) if total_tasks else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Subjects", total_subjects)
    c2.metric("Study tasks", total_tasks)
    c3.metric("Completed", completed_tasks)
    c4.metric("Pending", pending_tasks)
    st.progress(progress / 100 if total_tasks else 0)
    st.write(f"**Overall completion:** {progress:.1f}%")

    st.subheader("Recommended priorities")
    if subjects:
        ranked = sorted(subjects, key=lambda s: priority_score(s[2], s[3], s[4]), reverse=True)
        for subject in ranked[:5]:
            sid, name, exam_date, difficulty, preparation, weekly_hours = subject
            score = priority_score(exam_date, difficulty, preparation)
            days_left = (date.fromisoformat(exam_date) - date.today()).days
            st.write(f"**{name}** — priority score {score:.1f}; exam in {days_left} day(s); preparation {preparation}/10.")
    else:
        st.info("Add subjects in Manage Subjects to see your recommendations.")

    st.subheader("Upcoming study tasks")
    upcoming = [task for task in tasks if task[3] >= date.today().isoformat() and task[5] == 0]
    if upcoming:
        for task in upcoming[:8]:
            st.write(f"• {task[3]} — **{task[1]}**: {task[2]} ({task[4]:g} hour)")
    else:
        st.info("No pending future tasks. Generate a study plan to get started.")

elif page == "Manage Subjects":
    st.subheader("Add a subject")
    with st.form("subject_form", clear_on_submit=True):
        name = st.text_input("Subject name", placeholder="e.g., Data Structures")
        exam_date = st.date_input("Exam date", value=date.today() + timedelta(days=14), min_value=date.today())
        difficulty = st.slider("Difficulty (1 = easy, 10 = very difficult)", 1, 10, 5)
        preparation = st.slider("Current preparation (1 = very low, 10 = fully prepared)", 1, 10, 4)
        weekly_hours = st.number_input("Target study hours per week", min_value=1.0, max_value=60.0, value=5.0, step=1.0)
        submitted = st.form_submit_button("Save Subject")
        if submitted:
            if not name.strip():
                st.error("Please enter a subject name.")
            else:
                try:
                    with get_connection() as conn:
                        conn.execute(
                            "INSERT INTO subjects (name, exam_date, difficulty, preparation, weekly_hours) VALUES (?, ?, ?, ?, ?)",
                            (name.strip(), exam_date.isoformat(), difficulty, preparation, weekly_hours)
                        )
                    st.success(f"Subject '{name.strip()}' added.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That subject already exists. Use a different name.")

    st.subheader("Your subjects")
    subjects = fetch_subjects()
    if subjects:
        for subject in subjects:
            sid, name, exam, difficulty, preparation, weekly_hours = subject
            with st.expander(f"{name} — exam {exam}"):
                st.write(f"Difficulty: {difficulty}/10 | Preparation: {preparation}/10 | Target: {weekly_hours:g} hours/week")
                if st.button(f"Delete {name}", key=f"delete_subject_{sid}"):
                    with get_connection() as conn:
                        conn.execute("DELETE FROM tasks WHERE subject_id = ?", (sid,))
                        conn.execute("DELETE FROM subjects WHERE id = ?", (sid,))
                    st.success("Subject and its tasks deleted.")
                    st.rerun()
    else:
        st.info("No subjects added yet.")

elif page == "Generate Study Plan":
    st.subheader("Create a personalized study plan")
    subjects = fetch_subjects()
    if not subjects:
        st.warning("Add at least one subject in Manage Subjects first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            days = st.number_input("Plan length (days)", min_value=1, max_value=30, value=7)
        with col2:
            hours_per_day = st.number_input("Study hours available per day", min_value=1.0, max_value=12.0, value=2.0, step=0.5)
        st.write("The planner gives higher priority to subjects with closer exams, greater difficulty, and lower preparation.")
        if st.button("Generate My Plan", type="primary"):
            plan = generate_plan(subjects, int(days), float(hours_per_day))
            with get_connection() as conn:
                for sid, name, title, task_date, duration in plan:
                    conn.execute(
                        "INSERT INTO tasks (subject_id, title, task_date, duration) VALUES (?, ?, ?, ?)",
                        (sid, title, task_date, duration)
                    )
            st.success(f"Created {len(plan)} study sessions. Open My Tasks to view them.")
            st.rerun()

elif page == "My Tasks":
    st.subheader("Study tasks")
    tasks = fetch_tasks()
    if not tasks:
        st.info("No tasks yet. Add subjects and generate a study plan.")
    else:
        filter_choice = st.selectbox("Show tasks", ["All", "Pending", "Completed"])
        filtered = [t for t in tasks if filter_choice == "All" or (filter_choice == "Pending" and t[5] == 0) or (filter_choice == "Completed" and t[5] == 1)]
        for task in filtered:
            task_id, subject_name, title, task_date, duration, completed, subject_id = task
            cols = st.columns([0.7, 3, 1.2, 1])
            cols[0].write("✅" if completed else "🕒")
            cols[1].write(f"**{subject_name}** — {title}\n\n{task_date} · {duration:g} hour")
            if not completed:
                if cols[3].button("Complete", key=f"complete_{task_id}"):
                    with get_connection() as conn:
                        conn.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
                    st.rerun()
            else:
                cols[3].write("Done")
        st.divider()
        if st.button("Delete all study tasks"):
            with get_connection() as conn:
                conn.execute("DELETE FROM tasks")
            st.success("All tasks deleted.")
            st.rerun()

elif page == "About Project":
    st.subheader("Project overview")
    st.markdown("""
    **Problem:** Students may find it difficult to prioritize subjects and organize study time before exams.

    **Proposed solution:** This application stores subjects, considers exam dates, difficulty, and preparation level, and creates a study plan with task tracking.

    **Core modules:**
    1. Subject management
    2. Priority recommendation engine
    3. Study-plan generator
    4. Task completion tracking
    5. Progress dashboard

    **Important:** The current version uses a rule-based recommendation algorithm. It is an educational prototype and does not use a trained machine-learning model or guarantee better exam results.
    """)
    st.subheader("Priority score")
    st.latex(r"\text{Priority Score} = 0.5(\text{Urgency}) + 2(\text{Difficulty}) + 0.8(10 - \text{Preparation})")
    st.write("Higher scores indicate subjects that may need more attention. The urgency value increases as the exam date gets closer.")
