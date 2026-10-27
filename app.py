
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
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QuizBank | V2 Manager</title>
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
.brand { font-size: 25px; font-weight: 800; }
header p { color: #e8e4ff; }
.container { max-width: 1100px; margin: 32px auto; padding: 0 20px; }
.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
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
.stat h2 { margin-bottom: 0; font-size: 28px; }
.accent { color: #6d4aff; }
.panel { margin-bottom: 25px; }
.panel h2 { margin-top: 0; }
.form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}
.full { grid-column: 1 / -1; }
label { display: block; font-weight: 600; margin-bottom: 7px; }
input, textarea, select {
    width: 100%;
    padding: 12px;
    border: 1px solid #dfe1ee;
    border-radius: 9px;
    font: inherit;
    background: white;
}
textarea { min-height: 90px; resize: vertical; }
input:focus, textarea:focus, select:focus {
    outline: 2px solid #c4b5fd;
    border-color: #8b5cf6;
}
button, .button {
    display: inline-block;
    border: 0;
    border-radius: 9px;
    padding: 11px 16px;
    font-weight: 700;
    cursor: pointer;
    text-decoration: none;
    font-size: 14px;
}
.primary {
    color: white;
    background: linear-gradient(100deg, #5145cd, #8b5cf6);
}
.secondary { background: #eee9ff; color: #5941bd; }
.danger { background: #fff0f0; color: #b42332; }
.question-card { margin-top: 14px; }
.question-title { font-size: 17px; font-weight: 700; }
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
    overflow-wrap: anywhere;
}
.correct { color: #087443; font-weight: 700; }
.tag {
    display: inline-block;
    background: #eee9ff;
    color: #5941bd;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}
.actions { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 15px; }
.empty { text-align: center; color: #8588a0; padding: 25px; }
.notice {
    padding: 12px 15px;
    border-radius: 9px;
    background: #ecfdf3;
    color: #087443;
    margin-bottom: 18px;
}
footer { text-align: center; padding: 25px; color: #8588a0; }
@media (max-width: 600px) {
    .form-grid, .options { grid-template-columns: 1fr; }
    .full { grid-column: auto; }
    header { padding: 24px 20px; }
}
</style>
</head>
<body>
<header>
    <div class="brand">✦ QuizBank</div>
    <h1>Question Bank Dashboard</h1>
    <p>Version 2 — Add, edit and delete questions.</p>
</header>

<main class="container">
    {% if message %}
    <div class="notice">{{ message }}</div>
    {% endif %}

    <section class="stats">
        <div class="stat">
            <small>Total Questions</small>
            <h2 class="accent">{{ questions|length }}</h2>
        </div>
        <div class="stat">
            <small>Application Version</small>
            <h2>V2</h2>
        </div>
        <div class="stat">
            <small>Features</small>
            <h2 style="font-size:20px">Add · Edit · Delete</h2>
        </div>
    </section>

    <section class="panel">
        <h2>＋ Add a New Question</h2>
        <p style="color:#777b96">Enter the question and four answer choices.</p>
        <form method="POST" action="{{ url_for('add_question') }}">
            <div class="form-grid">
                <div class="full">
                    <label for="question">Question</label>
                    <textarea id="question" name="question"
                        placeholder="Type your question..." required></textarea>
                </div>
                <div><label for="a">Option A</label><input id="a" name="a" required></div>
                <div><label for="b">Option B</label><input id="b" name="b" required></div>
                <div><label for="c">Option C</label><input id="c" name="c" required></div>
                <div><label for="d">Option D</label><input id="d" name="d" required></div>
                <div class="full">
                    <label for="answer">Correct Answer</label>
                    <select id="answer" name="answer" required>
                        <option value="">Select correct option</option>
                        <option value="A">Option A</option>
                        <option value="B">Option B</option>
                        <option value="C">Option C</option>
                        <option value="D">Option D</option>
                    </select>
                </div>
                <div class="full">
                    <button class="primary" type="submit">＋ Add Question</button>
                </div>
            </div>
        </form>
    </section>

    <section>
        <h2>Saved Questions</h2>
        <p style="color:#777b96">Edit details or remove a question below.</p>

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
            <p class="correct">✓ Correct answer: {{ q.answer }}</p>
            <div class="actions">
                <a class="button secondary"
                   href="{{ url_for('edit_question', question_id=q.id) }}">✎ Edit</a>
                <form method="POST"
                      action="{{ url_for('delete_question', question_id=q.id) }}"
                      onsubmit="return confirm('Delete this question permanently?');">
                    <button class="danger" type="submit">Delete</button>
                </form>
            </div>
        </article>
        {% else %}
        <div class="question-card empty">No questions yet. Add your first question above.</div>
        {% endfor %}
    </section>
</main>
<footer>QuizBank · Quiz Question Bank System · Version 2</footer>
</body>
</html>
"""


EDIT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Edit Question | QuizBank</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: "Segoe UI", Arial, sans-serif;
       background: #f4f5fb; color: #202344; }
header { background: linear-gradient(120deg, #312e81, #6d4aff, #8b5cf6);
         color: white; padding: 25px 6%; }
main { max-width: 850px; margin: 30px auto; padding: 0 20px; }
.panel { background: white; border-radius: 16px; padding: 25px;
         box-shadow: 0 5px 24px #29265b0c; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; }
.full { grid-column: 1 / -1; }
label { display: block; font-weight: 600; margin-bottom: 7px; }
input, textarea, select { width: 100%; padding: 12px; border: 1px solid #dfe1ee;
    border-radius: 9px; font: inherit; background: white; }
textarea { min-height: 90px; }
button, a { display: inline-block; padding: 12px 18px; border: 0;
    border-radius: 9px; font-weight: 700; text-decoration: none; cursor: pointer; }
button { color: white; background: linear-gradient(100deg,#5145cd,#8b5cf6); }
a { background: #eee9ff; color: #5941bd; }
@media(max-width:600px) { .grid { grid-template-columns: 1fr; } .full { grid-column:auto; } }
</style>
</head>
<body>
<header><h1>✎ Edit Question</h1><p>Update the question and save your changes.</p></header>
<main>
<section class="panel">
<form method="POST">
<div class="grid">
<div class="full">
<label for="question">Question</label>
<textarea id="question" name="question" required>{{ q.question }}</textarea>
</div>
<div><label for="a">Option A</label><input id="a" name="a" value="{{ q.a }}" required></div>
<div><label for="b">Option B</label><input id="b" name="b" value="{{ q.b }}" required></div>
<div><label for="c">Option C</label><input id="c" name="c" value="{{ q.c }}" required></div>
<div><label for="d">Option D</label><input id="d" name="d" value="{{ q.d }}" required></div>
<div class="full">
<label for="answer">Correct Answer</label>
<select id="answer" name="answer" required>
<option value="A" {% if q.answer == 'A' %}selected{% endif %}>Option A</option>
<option value="B" {% if q.answer == 'B' %}selected{% endif %}>Option B</option>
<option value="C" {% if q.answer == 'C' %}selected{% endif %}>Option C</option>
<option value="D" {% if q.answer == 'D' %}selected{% endif %}>Option D</option>
</select>
</div>
<div class="full">
<button type="submit">Save Changes</button>
<a href="{{ url_for('home') }}">Cancel</a>
</div>
</div>
</form>
</section>
</main>
</body>
</html>
"""


def get_question_data(form):
    question = form.get("question", "").strip()
    a = form.get("a", "").strip()
    b = form.get("b", "").strip()
    c = form.get("c", "").strip()
    d = form.get("d", "").strip()
    answer = form.get("answer", "").strip()

    if not all([question, a, b, c, d]):
        return None

    if answer not in ("A", "B", "C", "D"):
        return None

    return question, a, b, c, d, answer


@app.route("/")
def home():
    with get_db_connection() as conn:
        questions = conn.execute(
            "SELECT * FROM questions ORDER BY id DESC"
        ).fetchall()

    message = request.args.get("message", "")
    return render_template_string(
        HTML, questions=questions, message=message
    )


@app.route("/add", methods=["POST"])
def add_question():
    data = get_question_data(request.form)
    if data is None:
        return "All fields are required and the correct answer must be A, B, C or D.", 400

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO questions (question, a, b, c, d, answer)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)

    return redirect(url_for("home", message="Question added successfully."))


@app.route("/edit/<int:question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    with get_db_connection() as conn:
        q = conn.execute(
            "SELECT * FROM questions WHERE id = ?", (question_id,)
        ).fetchone()

    if q is None:
        return "Question not found.", 404

    if request.method == "POST":
        data = get_question_data(request.form)
        if data is None:
            return "All fields are required and the correct answer must be A, B, C or D.", 400

        with get_db_connection() as conn:
            conn.execute("""
                UPDATE questions
                SET question = ?, a = ?, b = ?, c = ?, d = ?, answer = ?
                WHERE id = ?
            """, (*data, question_id))

        return redirect(url_for("home", message="Question updated successfully."))

    return render_template_string(EDIT_HTML, q=q)


@app.route("/delete/<int:question_id>", methods=["POST"])
def delete_question(question_id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))

    return redirect(url_for("home", message="Question deleted successfully."))


if __name__ == "__main__":
    app.run(debug=True)
