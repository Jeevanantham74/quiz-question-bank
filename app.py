
from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
DATABASE = "questions.db"


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
            )
        """)


def get_question_data(form):
    question = form.get("question", "").strip()
    a = form.get("a", "").strip()
    b = form.get("b", "").strip()
    c = form.get("c", "").strip()
    d = form.get("d", "").strip()
    answer = form.get("answer", "").strip().upper()

    if not all([question, a, b, c, d]) or answer not in ["A", "B", "C", "D"]:
        return None

    return question, a, b, c, d, answer


FORM_FIELDS = """
<label>Question</label>
<textarea name="question" required>{{ q.question if q else '' }}</textarea>

<label>Option A</label>
<input name="a" value="{{ q.a if q else '' }}" required>

<label>Option B</label>
<input name="b" value="{{ q.b if q else '' }}" required>

<label>Option C</label>
<input name="c" value="{{ q.c if q else '' }}" required>

<label>Option D</label>
<input name="d" value="{{ q.d if q else '' }}" required>

<label>Correct Answer</label>
<select name="answer" required>
    {% for option in ['A', 'B', 'C', 'D'] %}
    <option value="{{ option }}"
        {% if q and q.answer == option %}selected{% endif %}>
        {{ option }}
    </option>
    {% endfor %}
</select>
"""


PAGE_STYLE = """
<style>
* { box-sizing: border-box; }
body {
    margin: 0; font-family: Arial, sans-serif; color: #20243a;
    background: linear-gradient(135deg, #eef2ff, #f8faff);
}
.container { max-width: 1050px; margin: 35px auto; padding: 20px; }
header {
    padding: 28px; border-radius: 18px; color: white;
    background: linear-gradient(120deg, #4338ca, #7c3aed);
    margin-bottom: 24px;
}
header h1 { margin: 0 0 8px; }
header p { margin: 0; opacity: .9; }
.panel {
    background: white; border-radius: 16px; padding: 24px;
    margin-bottom: 24px; box-shadow: 0 6px 22px #252d5010;
}
label { display: block; font-weight: bold; margin: 14px 0 6px; }
input, textarea, select {
    width: 100%; padding: 11px; border: 1px solid #d5d9e8;
    border-radius: 8px; font: inherit; background: white;
}
textarea { min-height: 75px; resize: vertical; }
button, .button {
    display: inline-block; border: 0; border-radius: 8px;
    padding: 10px 15px; background: #5145cd; color: white;
    cursor: pointer; text-decoration: none; font-size: 14px;
}
button:hover, .button:hover { opacity: .88; }
.search-row { display: flex; gap: 10px; margin-top: 12px; }
.search-row input { flex: 1; min-width: 0; }
.question-card {
    border: 1px solid #e7e9f2; border-radius: 12px;
    padding: 18px; margin-top: 15px;
}
.question-card h3 { margin-top: 0; line-height: 1.5; }
.options { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
.option { padding: 10px; background: #f5f6fc; border-radius: 7px; }
.correct { color: #167347; font-weight: bold; margin: 12px 0; }
.actions { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.delete { background: #dc3545; }
.notice { padding: 12px; border-radius: 8px; background: #e7f7ed; color: #17653b; }
.muted { color: #686d82; }
@media(max-width: 600px) {
    .container { margin: 10px auto; padding: 12px; }
    .options { grid-template-columns: 1fr; }
    .search-row { flex-direction: column; }
}
</style>
"""


EDIT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Edit Question</title>
""" + PAGE_STYLE + """
</head>
<body>
<div class="container">
<header><h1>Edit Question</h1><p>Update your question bank</p></header>
<div class="panel">
<form method="POST">
""" + FORM_FIELDS + """
<div class="actions">
<button type="submit">Save Changes</button>
<a class="button" href="{{ url_for('home') }}">Cancel</a>
</div>
</form>
</div>
</div>
</body>
</html>
"""


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quiz Question Bank</title>
""" + PAGE_STYLE + """
</head>
<body>
<div class="container">
<header>
    <h1>Quiz Question Bank</h1>
    <p>Manage, search, and organize your multiple-choice questions.</p>
</header>

{% if message %}
<div class="notice">{{ message }}</div>
{% endif %}

<div class="panel">
<h2>Add a New Question</h2>
<form method="POST" action="{{ url_for('add_question') }}">
""" + FORM_FIELDS + """
<div class="actions"><button type="submit">Add Question</button></div>
</form>
</div>

<div class="panel">
<h2>Search Questions</h2>
<form method="GET" action="{{ url_for('home') }}">
<div class="search-row">
    <input type="search" name="q" placeholder="Search question text or options..."
           value="{{ search_query }}" aria-label="Search questions">
    <button type="submit">Search</button>
    {% if search_query %}
    <a class="button" href="{{ url_for('home') }}">Clear</a>
    {% endif %}
</div>
</form>
<p class="muted">
Showing {{ questions|length }} question(s)
{% if search_query %} matching "{{ search_query }}"{% endif %}.
</p>

{% for item in questions %}
<div class="question-card">
    <h3>{{ loop.index }}. {{ item.question }}</h3>
    <div class="options">
        <div class="option"><strong>A.</strong> {{ item.a }}</div>
        <div class="option"><strong>B.</strong> {{ item.b }}</div>
        <div class="option"><strong>C.</strong> {{ item.c }}</div>
        <div class="option"><strong>D.</strong> {{ item.d }}</div>
    </div>
    <p class="correct">Correct Answer: {{ item.answer }}</p>
    <div class="actions">
        <a class="button" href="{{ url_for('edit_question', question_id=item.id) }}">Edit</a>
        <form method="POST" action="{{ url_for('delete_question', question_id=item.id) }}"
              onsubmit="return confirm('Delete this question permanently?');">
            <button class="delete" type="submit">Delete</button>
        </form>
    </div>
</div>
{% else %}
<p class="muted">No questions found. Try another keyword or add a question.</p>
{% endfor %}
</div>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    search_query = request.args.get("q", "").strip()

    with get_db_connection() as conn:
        if search_query:
            pattern = f"%{search_query}%"
            questions = conn.execute("""
                SELECT * FROM questions
                WHERE question LIKE ?
                   OR a LIKE ?
                   OR b LIKE ?
                   OR c LIKE ?
                   OR d LIKE ?
                ORDER BY id DESC
            """, (pattern, pattern, pattern, pattern, pattern)).fetchall()
        else:
            questions = conn.execute(
                "SELECT * FROM questions ORDER BY id DESC"
            ).fetchall()

    return render_template_string(
        HTML,
        questions=questions,
        search_query=search_query,
        message=request.args.get("message", "")
    )


@app.route("/add", methods=["POST"])
def add_question():
    data = get_question_data(request.form)
    if data is None:
        return "Please complete all fields and choose answer A, B, C or D.", 400

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
            return "Please complete all fields and choose answer A, B, C or D.", 400

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
    init_db()
    app.run(debug=True)
