import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for, session, flash)


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "ai-study-companion-secret-key"
)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "database.db"
)


# =========================================================
# OPTIONAL AI
# =========================================================

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6"
)


def ai_request(instruction):
    """
    Optional AI function.

    If OPENAI_API_KEY is not available,
    the project automatically uses local fallback functions.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or OpenAI is None:
        return None

    try:

        client = OpenAI(
            api_key=api_key
        )

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=instruction
        )

        return response.output_text.strip()

    except Exception:

        return None


# =========================================================
# DATABASE
# =========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def create_tables():

    conn = get_db()

    # USERS
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            bio TEXT DEFAULT '',

            college TEXT DEFAULT '',

            branch TEXT DEFAULT '',

            address TEXT DEFAULT ''

        )
    """)


    # Add profile fields to existing databases
    for column in ["bio", "college", "branch", "address"]:
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {column} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass


    # QUIZ RESULTS
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            score INTEGER NOT NULL,

            total INTEGER NOT NULL,

            date TEXT NOT NULL

        )
    """)


    # STUDY SESSIONS
    conn.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            minutes INTEGER NOT NULL,

            date TEXT NOT NULL

        )
    """)


    conn.commit()

    conn.close()


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return view(
            *args,
            **kwargs
        )

    return wrapped_view


# =========================================================
# LOCAL SUMMARY
# =========================================================

def local_summary(text):

    cleaned = " ".join(
        text.split()
    )

    if not cleaned:
        return ""


    sentences = [
        s.strip()
        for s in cleaned
        .replace("!", ".")
        .replace("?", ".")
        .split(".")
        if s.strip()
    ]


    if len(sentences) <= 3:

        return ". ".join(
            sentences
        ) + "."


    return ". ".join(
        sentences[:3]
    ) + "."


# =========================================================
# LOCAL EXPLANATION
# =========================================================

def local_explanation(topic, level):

    key = topic.lower().strip()


    content = {

        "python": {

            "beginner":
            """
Python is a high-level programming language
known for simple and readable syntax.

It is used for web development, automation,
data science and artificial intelligence.
""",

            "intermediate":
            """
Python is an interpreted, general-purpose
programming language.

It supports object-oriented, procedural
and functional programming.
"""
        },


        "html": {

            "beginner":
            """
HTML stands for HyperText Markup Language.

It is used to create the structure
of web pages.

HTML provides headings, paragraphs,
links, images and forms.
""",

            "intermediate":
            """
HTML provides the structural foundation
of a web application.

Semantic elements such as header, nav,
main, section and footer organize content.
"""
        },


        "css": {

            "beginner":
            """
CSS stands for Cascading Style Sheets.

It is used to design HTML web pages.

CSS controls colors, fonts, spacing,
layouts and animations.
""",

            "intermediate":
            """
CSS controls the presentation and layout
of web pages.

It provides Flexbox, Grid, media queries,
transitions and responsive design.
"""
        },


        "javascript": {

            "beginner":
            """
JavaScript makes web pages interactive.

It can respond to button clicks,
change page content and validate forms.
""",

            "intermediate":
            """
JavaScript provides dynamic behaviour
through the DOM, events, functions,
objects and asynchronous programming.
"""
        },


        "database": {

            "beginner":
            """
A database stores and manages information.

For example, a student database can store
names, emails, marks and study information.
""",

            "intermediate":
            """
A relational database stores information
in tables containing rows and columns.

SQL is commonly used to create,
read, update and delete data.
"""
        },


        "flask": {

            "beginner":
            """
Flask is a lightweight Python web framework.

It connects URLs with Python functions
and can render HTML templates.
""",

            "intermediate":
            """
Flask provides routing, request handling,
sessions and template rendering for
Python web applications.
"""
        }

    }


    if key in content:

        return content[key].get(
            level,
            content[key]["beginner"]
        )


    return f"""
{topic} is an important study topic.

Start by understanding its definition,
main concepts and practical applications.

Then practice the topic with examples
and revision questions.
"""


# =========================================================
# MCQ GENERATOR
# =========================================================

def generate_mcqs(topic):

    topic = topic.strip()


    mcqs = [

        {
            "question":
            f"What is the best way to learn {topic}?",

            "options": [

                "Practice and revision",

                "Ignore examples",

                "Avoid practice",

                "Guess everything"

            ],

            "answer":
            "Practice and revision"
        },


        {
            "question":
            f"What should you understand first in {topic}?",

            "options": [

                "Basic concepts",

                "Only advanced topics",

                "Nothing",

                "Random facts"

            ],

            "answer":
            "Basic concepts"
        },


        {
            "question":
            f"What improves your knowledge of {topic}?",

            "options": [

                "Regular practice",

                "Never studying",

                "Ignoring mistakes",

                "Avoiding examples"

            ],

            "answer":
            "Regular practice"
        },


        {
            "question":
            f"Why is learning {topic} useful?",

            "options": [

                "It develops knowledge and skills",

                "It wastes all time",

                "It has no use",

                "It prevents learning"

            ],

            "answer":
            "It develops knowledge and skills"
        },


        {
            "question":
            f"What is important while studying {topic}?",

            "options": [

                "Practice and understanding",

                "Only memorization",

                "Skipping basics",

                "Not solving questions"

            ],

            "answer":
            "Practice and understanding"
        }

    ]


    return mcqs


# =========================================================
# INDEX
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        if not name or not email or not password:

            flash(
                "Please fill all fields.",
                "error"
            )

            return render_template(
                "register.html"
            )


        conn = get_db()


        try:

            conn.execute(
                """
                INSERT INTO users
                (name, email, password)

                VALUES (?, ?, ?)
                """,

                (
                    name,
                    email,
                    password
                )
            )

            conn.commit()


        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "This email is already registered.",
                "error"
            )

            return render_template(
                "register.html"
            )


        conn.close()


        flash(
            "Account created successfully. Please login.",
            "success"
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        conn = get_db()


        user = conn.execute(
            """
            SELECT *

            FROM users

            WHERE email = ?
            AND password = ?
            """,

            (
                email,
                password
            )
        ).fetchone()


        conn.close()


        if user:

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]


            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid email or password.",
            "error"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]


    conn = get_db()


    quiz_count = conn.execute(
        """
        SELECT COUNT(*) AS count

        FROM quiz_results

        WHERE user_id = ?
        """,

        (user_id,)
    ).fetchone()["count"]


    best_score = conn.execute(
        """
        SELECT

        MAX(
            CAST(score AS REAL)
            / NULLIF(total, 0)
            * 100
        ) AS best

        FROM quiz_results

        WHERE user_id = ?
        """,

        (user_id,)
    ).fetchone()["best"]


    study_minutes = conn.execute(
        """
        SELECT
        COALESCE(
            SUM(minutes),
            0
        ) AS total

        FROM study_sessions

        WHERE user_id = ?
        """,

        (user_id,)
    ).fetchone()["total"]


    conn.close()


    return render_template(

        "dashboard.html",

        user_name=session["user_name"],

        quiz_count=quiz_count,

        best_score=(
            round(best_score)
            if best_score is not None
            else 0
        ),

        study_minutes=study_minutes

    )

# =========================================================
# MY PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()

    # Get user details
    user = conn.execute(
        """
        SELECT id, name, email, bio, college, branch, address
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    # Get quiz statistics
    quiz_stats = conn.execute(
        """
        SELECT
            COUNT(*) AS total_quizzes,
            COALESCE(SUM(score), 0) AS total_score,
            COALESCE(SUM(total), 0) AS total_questions
        FROM quiz_results
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    # Get best quiz score
    best_score = conn.execute(
        """
        SELECT score, total
        FROM quiz_results
        WHERE user_id = ?
        ORDER BY score DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    # Quiz information
    total_quizzes = quiz_stats["total_quizzes"]
    total_score = quiz_stats["total_score"]
    total_questions = quiz_stats["total_questions"]

    # Calculate percentage
    if total_questions > 0:
        average_score = round(
            (total_score / total_questions) * 100
        )
    else:
        average_score = 0

    # Best score
    if best_score:
        best_percentage = round(
            (best_score["score"] / best_score["total"]) * 100
        )
    else:
        best_percentage = 0

    return render_template(
        "profile.html",
        user=user,
        total_quizzes=total_quizzes,
        average_score=average_score,
        best_percentage=best_percentage
    )
# =========================================================
# edit_profile
# =========================================================

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    user_id = session["user_id"]

    conn = get_db()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        bio = request.form.get("bio", "").strip()
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "").strip()
        address = request.form.get("address", "").strip()

        conn.execute(
            """
            UPDATE users
            SET name = ?,
                email = ?,
                bio = ?,
                college = ?,
                branch = ?,
                address = ?
            WHERE id = ?
            """,
            (
                name,
                email,
                bio,
                college,
                branch,
                address,
                user_id
            )
        )

        conn.commit()
        conn.close()

        session["user_name"] = name

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("profile")
        )

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_profile.html",
        user=user
    )

# =========================================================
# AI SUMMARY
# =========================================================

@app.route(
    "/summary",
    methods=["GET", "POST"]
)
@login_required
def summary():

    summary_text = ""

    original_text = ""


    if request.method == "POST":

        original_text = request.form.get(
            "text",
            ""
        ).strip()


        if original_text:

            prompt = f"""
You are an educational study assistant.

Summarize the following study material
in simple student-friendly language.

Give:
1. A short heading
2. Important points
3. Easy revision points

Do not add information that is
not present in the material.

Study material:

{original_text}
"""


            summary_text = (
                ai_request(prompt)
                or local_summary(original_text)
            )


        else:

            flash(
                "Please enter study material.",
                "warning"
            )


    return render_template(

        "summary.html",

        summary_text=summary_text,

        original_text=original_text

    )


# =========================================================
# MCQ
# =========================================================

@app.route(
    "/mcq",
    methods=["GET", "POST"]
)
@login_required
def mcq():

    mcqs = []

    topic = ""


    if request.method == "POST":

        topic = request.form.get(
            "topic",
            ""
        ).strip()


        if topic:

            # -----------------------------------------
            # ALWAYS CREATE LOCAL MCQs FIRST
            # -----------------------------------------

            mcqs = generate_mcqs(topic)


            # -----------------------------------------
            # OPTIONAL AI MCQs
            # -----------------------------------------

            prompt = f"""
Create exactly 5 beginner-friendly
multiple-choice questions about:

{topic}

For each question give:

Question
A) option
B) option
C) option
D) option
Answer: complete correct option text

Do not add explanations.
"""


            ai_text = ai_request(prompt)


            # -----------------------------------------
            # If AI response is valid, use it
            # -----------------------------------------

            if ai_text:

                ai_mcqs = []

                blocks = [
                    block.strip()
                    for block in ai_text.split("\n\n")
                    if block.strip()
                ]


                for block in blocks:

                    lines = [
                        line.strip()
                        for line in block.splitlines()
                        if line.strip()
                    ]


                    if len(lines) < 6:

                        continue


                    question = lines[0]


                    if ":" in question:

                        question = question.split(
                            ":",
                            1
                        )[1].strip()


                    options = []


                    for line in lines:

                        upper = line.upper()


                        if (
                            upper.startswith("A)")
                            or upper.startswith("B)")
                            or upper.startswith("C)")
                            or upper.startswith("D)")
                        ):

                            options.append(
                                line[2:].strip()
                            )


                    answer = ""


                    for line in lines:

                        if line.lower().startswith(
                            "answer:"
                        ):

                            answer = line.split(
                                ":",
                                1
                            )[1].strip()

                            break


                    if (
                        len(options) == 4
                        and answer
                    ):

                        ai_mcqs.append({

                            "question":
                            question,

                            "options":
                            options,

                            "answer":
                            answer

                        })


                if len(ai_mcqs) >= 1:

                    mcqs = ai_mcqs[:5]


    # =====================================================
    # IMPORTANT FIX
    # =====================================================
    #
    # We send BOTH:
    #
    # mcqs
    # questions
    #
    # So template variable mismatch will NOT happen.
    # =====================================================

    return render_template(

        "mcq.html",

        mcqs=mcqs,

        questions=mcqs,

        topic=topic

    )


# =========================================================
# QUIZ
# =========================================================

@app.route(
    "/quiz",
    methods=["GET", "POST"]
)
@login_required
def quiz():

    questions = [

        {
            "question":
            "Which language is used with Flask?",

            "options": [
                "Python",
                "Java",
                "C++",
                "PHP"
            ],

            "answer":
            "Python"
        },


        {
            "question":
            "Which technology is used to style a webpage?",

            "options": [
                "HTML",
                "CSS",
                "Python",
                "SQL"
            ],

            "answer":
            "CSS"
        },


        {
            "question":
            "Which technology makes webpages interactive?",

            "options": [
                "HTML",
                "CSS",
                "JavaScript",
                "SQLite"
            ],

            "answer":
            "JavaScript"
        },


        {
            "question":
            "Which database is used in this project?",

            "options": [
                "MongoDB",
                "MySQL",
                "SQLite",
                "Oracle"
            ],

            "answer":
            "SQLite"
        },


        {
            "question":
            "What does HTML stand for?",

            "options": [

                "HyperText Markup Language",

                "HighText Machine Language",

                "Hyper Tool Multi Language",

                "Home Tool Markup Language"

            ],

            "answer":
            "HyperText Markup Language"
        }

    ]


    if request.method == "POST":

        score = 0


        for i, question in enumerate(
            questions
        ):

            selected = request.form.get(
                f"question{i}"
            )


            if selected == question["answer"]:

                score += 1


        conn = get_db()


        conn.execute(
            """
            INSERT INTO quiz_results

            (user_id, score, total, date)

            VALUES (?, ?, ?, ?)
            """,

            (
                session["user_id"],

                score,

                len(questions),

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )


        conn.commit()

        conn.close()


        return render_template(

            "quiz_result.html",

            score=score,

            total=len(questions)

        )


    return render_template(

        "quiz.html",

        questions=questions

    )


# =========================================================
# TRANSLATE
# =========================================================

@app.route(
    "/translate",
    methods=["GET", "POST"]
)
@login_required
def translate():

    translated_text = ""

    selected_language = "English"

    original_text = ""


    if request.method == "POST":

        original_text = request.form.get(
            "text",
            ""
        ).strip()


        selected_language = request.form.get(
            "language",
            "English"
        )


        if original_text:

            prompt = f"""
Translate the following study material
into {selected_language}.

Return only the translated text.

Text:

{original_text}
"""


            translated_text = ai_request(
                prompt
            )


            if not translated_text:

                if selected_language == "English":

                    translated_text = original_text

                else:

                    translated_text = (
                        "AI translation is not configured. "
                        "Add OPENAI_API_KEY for real translation."
                    )


    return render_template(

        "translate.html",

        translated_text=translated_text,

        selected_language=selected_language,

        original_text=original_text

    )


# =========================================================
# READ ALOUD
# =========================================================

@app.route("/read-aloud")
@login_required
def read_aloud():

    return render_template(
        "read_aloud.html"
    )


# =========================================================
# EXPLAIN TOPIC
# =========================================================

@app.route(
    "/explain",
    methods=["GET", "POST"]
)
@login_required
def explain():

    explanation = ""

    topic = ""

    level = "beginner"


    if request.method == "POST":

        topic = request.form.get(
            "topic",
            ""
        ).strip()


        level = request.form.get(
            "level",
            "beginner"
        )


        if topic:

            prompt = f"""
You are an educational AI tutor.

Explain the topic:

{topic}

Level:
{level}

Give:

1. Simple definition
2. Main points
3. Practical example
4. Revision points

Use easy student-friendly language.
"""


            explanation = (
                ai_request(prompt)
                or local_explanation(
                    topic,
                    level
                )
            )


    return render_template(

        "explain.html",

        explanation=explanation,

        topic=topic,

        level=level

    )


# =========================================================
# TIMER
# =========================================================

@app.route("/timer")
@login_required
def timer():

    return render_template(
        "timer.html"
    )


# =========================================================
# SAVE TIMER
# =========================================================

@app.route(
    "/timer/save",
    methods=["POST"]
)
@login_required
def save_timer():

    try:

        minutes = int(
            request.form.get(
                "minutes",
                0
            )
        )

    except ValueError:

        minutes = 0


    if minutes > 0:

        conn = get_db()


        conn.execute(
            """
            INSERT INTO study_sessions

            (user_id, minutes, date)

            VALUES (?, ?, ?)
            """,

            (
                session["user_id"],

                minutes,

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )


        conn.commit()

        conn.close()


    return redirect(
        url_for("timer")
    )


@app.route("/achievements")
@login_required
def achievements():

    user_id = session["user_id"]

    conn = get_db()

    results = conn.execute(
        """
        SELECT score, total
        FROM quiz_results
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    study_minutes = conn.execute(
        """
        SELECT COALESCE(SUM(minutes), 0) AS total
        FROM study_sessions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()["total"]

    conn.close()

    quiz_count = len(results)

    # =========================================
    # CHECK UNLOCKED ACHIEVEMENTS
    # =========================================

    first_quiz = quiz_count >= 1

    quiz_master = quiz_count >= 5

    perfect_score = any(
        r["total"] > 0 and
        r["score"] == r["total"]
        for r in results
    )

    high_scorer = any(
        r["total"] > 0 and
        (r["score"] / r["total"]) * 100 >= 80
        for r in results
    )

    study_starter = study_minutes >= 25

    focused_learner = study_minutes >= 120


    # =========================================
    # ALL ACHIEVEMENTS
    # =========================================

    achievements = [

        {
            "name": "First Quiz",
            "icon": "🏆",
            "description": "Complete your first quiz.",
            "unlocked": first_quiz
        },

        {
            "name": "Quiz Master",
            "icon": "⭐",
            "description": "Complete 5 quizzes.",
            "unlocked": quiz_master
        },

        {
            "name": "Perfect Score",
            "icon": "💯",
            "description": "Get 100% in any quiz.",
            "unlocked": perfect_score
        },

        {
            "name": "High Scorer",
            "icon": "🔥",
            "description": "Score 80% or more in a quiz.",
            "unlocked": high_scorer
        },

        {
            "name": "Study Starter",
            "icon": "📚",
            "description": "Complete 25 minutes of study.",
            "unlocked": study_starter
        },

        {
            "name": "Focused Learner",
            "icon": "🎯",
            "description": "Complete 2 hours of study.",
            "unlocked": focused_learner
        }

    ]


    return render_template(

        "achievements.html",

        achievements=achievements,

        quiz_count=quiz_count,

        study_minutes=study_minutes

    )


# =========================================================
# CREATE DATABASE
# =========================================================

create_tables()


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )