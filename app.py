from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from pathlib import Path

app = Flask(__name__)

DATABASE = Path(__file__).with_name("questions.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                a TEXT NOT NULL,
                b TEXT NOT NULL,
                c TEXT NOT NULL,
                d TEXT NOT NULL,
                answer TEXT NOT NULL
                    CHECK (answer IN ('A', 'B', 'C', 'D'))
            )
        """)


init_db()


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QuizBank | Question Manager - V1</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: "Segoe UI", Arial, sans-serif;
    background: #f4f5fb;
    color: #202344;
}

header {
    background: linear-gradient(120deg, #312e81, #6d4aff, #8b5cf6);
    color: white;
    padding: 28px 6%;
}

.brand {
    font-size: 25px;
    font-weight: 800;
}

header p { color: #e8e4ff; }

.container {
    max-width: 1100px;
    margin: 32px auto;
    padding: 0 20px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 18px;
    margin-bottom: 25px;
}

.stat, .panel, .question-card {
    background: white;
    border-radius: 16px;
    padding: 23px;
    box-shadow: 0 5px 24px #29265b0c;
}

.stat small { color: #777b96; }

.stat h2 {
    margin-bottom: 0;
    font-size: 30px;
}

.accent { color: #6d4aff; }

.panel { margin-bottom: 25px; }

.panel h2 { margin-top: 0; }

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.full { grid-column: 1 / -1; }

label {
    display: block;
    font-weight: 600;
    margin-bottom: 7px;
}

input, textarea, select {
    width: 100%;
    padding: 12px;
    border: 1px solid #dfe1ee;
    border-radius: 9px;
    font: inherit;
    background: white;
}

textarea {
    min-height: 90px;
    resize: vertical;
}

input:focus, textarea:focus, select:focus {
    outline: 2px solid #c4b5fd;
    border-color: #8b5cf6;
}

button {
    border: 0;
    border-radius: 9px;
    padding: 13px 20px;
    font-weight: 700;
    cursor: pointer;
}

.primary {
    color: white;
    background: linear-gradient(100deg, #5145cd, #8b5cf6);
}

.primary:hover { filter: brightness(1.08); }

.question-card { margin-top: 14px; }

.question-title {
    font-size: 17px;
    font-weight: 700;
}

.options {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin-top: 15px;
}

.option {
    background: #f7f6ff;
    border: 1px solid #ece9ff;
    border-radius: 9px;
    padding: 12px;
}

.correct {
    color: #087443;
    font-weight: 700;
}

.tag {
    display: inline-block;
    background: #eee9ff;
    color: #5941bd;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}

.empty {
    text-align: center;
    color: #8588a0;
    padding: 25px;
}

footer {
    text-align: center;
    padding: 25px;
    color: #8588a0;
}

@media (max-width: 600px) {
    .form-grid, .options {
        grid-template-columns: 1fr;
    }

    .full { grid-column: auto; }

    header { padding: 24px 20px; }
}
</style>
</head>

<body>
<header>
    <div class="brand">✦ QuizBank</div>
    <h1>Question Bank Dashboard</h1>
    <p>Version 1 — Add Questions · Store Questions</p>
    <p>Manage your multiple-choice questions in one place.</p>
</header>

<main class="container">

    <section class="stats">
        <div class="stat">
            <small>Total Questions</small>
            <h2 class="accent">{{ questions|length }}</h2>
        </div>

        <div class="stat">
            <small>Application Version</small>
            <h2>V1</h2>
        </div>

        <div class="stat">
            <small>Module</small>
            <h2 style="font-size:22px">Add Questions</h2>
        </div>
    </section>

    <section class="panel">
        <h2>＋ Add a New Question</h2>
        <p style="color:#777b96">
            Enter the question and its four answer choices.
        </p>

        <form method="POST" action="/add">
            <div class="form-grid">

                <div class="full">
                    <label for="question">Question</label>
                    <textarea
                        id="question"
                        name="question"
                        placeholder="Type your question here..."
                        required
                    ></textarea>
                </div>

                <div>
                    <label for="option-a">Option A</label>
                    <input id="option-a" name="a" required>
                </div>

                <div>
                    <label for="option-b">Option B</label>
                    <input id="option-b" name="b" required>
                </div>

                <div>
                    <label for="option-c">Option C</label>
                    <input id="option-c" name="c" required>
                </div>

                <div>
                    <label for="option-d">Option D</label>
                    <input id="option-d" name="d" required>
                </div>

                <div class="full">
                    <label for="answer">Correct Answer</label>
                    <select id="answer" name="answer" required>
                        <option value="">Select the correct option</option>
                        <option value="A">Option A</option>
                        <option value="B">Option B</option>
                        <option value="C">Option C</option>
                        <option value="D">Option D</option>
                    </select>
                </div>

                <div class="full">
                    <button class="primary" type="submit">
                        ＋ Add Question
                    </button>
                </div>

            </div>
        </form>
    </section>

    <section>
        <h2>Saved Questions</h2>
        <p style="color:#777b96">Your question collection</p>

        {% for q in questions %}
        <article class="question-card">
            <span class="tag">QUESTION {{ q.id }}</span>

            <p class="question-title">{{ q.question }}</p>

            <div class="options">
                <div class="option">A. {{ q.a }}</div>
                <div class="option">B. {{ q.b }}</div>
                <div class="option">C. {{ q.c }}</div>
                <div class="option">D. {{ q.d }}</div>
            </div>

            <p class="correct">
                ✓ Correct answer: {{ q.answer }}
            </p>
        </article>

        {% else %}
        <div class="question-card empty">
            No questions yet. Add your first question above!
        </div>
        {% endfor %}
    </section>

</main>

<footer>
    QuizBank · Quiz Question Bank System · Version 1
</footer>
</body>
</html>
"""


@app.route("/")
def home():
    with get_db_connection() as conn:
        questions = conn.execute(
            "SELECT * FROM questions ORDER BY id DESC"
        ).fetchall()

    return render_template_string(HTML, questions=questions)


@app.route("/add", methods=["POST"])
def add_question():
    question = request.form.get("question", "").strip()
    a = request.form.get("a", "").strip()
    b = request.form.get("b", "").strip()
    c = request.form.get("c", "").strip()
    d = request.form.get("d", "").strip()
    answer = request.form.get("answer", "").strip()

    if not all([question, a, b, c, d]):
        return "All question and option fields are required.", 400

    if answer not in ("A", "B", "C", "D"):
        return "Please select a valid correct answer.", 400

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO questions
                (question, a, b, c, d, answer)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (question, a, b, c, d, answer))

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
