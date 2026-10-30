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


PAGE_STYLE = """
<style>
:root {
    --primary: #6c4cf1;
    --primary-dark: #5032d6;
    --ink: #252347;
    --muted: #777b96;
    --surface: #ffffff;
    --border: #e9e7f5;
}
* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: "Segoe UI", Arial, sans-serif;
    color: var(--ink);
    background:
        radial-gradient(ellipse at 5% 5%, #e0e7ff 0, transparent 38%),
        radial-gradient(ellipse at 95% 25%, #f3dfff 0, transparent 32%),
        linear-gradient(135deg, #f8f9ff, #f5f3ff);
    min-height: 100vh;
}

.container {
    max-width: 1100px;
    margin: auto;
    padding: 30px 22px 55px;
}

header {
    position: relative;
    overflow: hidden;
    padding: 35px;
    border-radius: 24px;
    color: white;
    background: linear-gradient(120deg, #4933c9, #7850ef 58%, #a855f7);
    box-shadow: 0 16px 35px #6546d52b;
    margin-bottom: 25px;
}

header::after {
    content: "";
    position: absolute;
    width: 200px;
    height: 200px;
    border: 35px solid #ffffff18;
    border-radius: 50%;
    right: -55px;
    top: -80px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 15px;
    position: relative;
    z-index: 1;
}

.logo {
    display: grid;
    place-items: center;
    width: 58px;
    height: 58px;
    border-radius: 17px;
    background: #ffffff24;
    font-size: 30px;
}

header h1 {
    margin: 0 0 9px;
    font-size: clamp(25px, 4vw, 36px);
    letter-spacing: -.7px;
}

header p {
    margin: 0;
    color: #eeeaff;
    line-height: 1.6;
}

.tagline {
    display: inline-block;
    margin-top: 23px;
    padding: 7px 12px;
    border: 1px solid #ffffff55;
    border-radius: 20px;
    font-size: 12px;
    letter-spacing: .4px;
    position: relative;
    z-index: 1;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 24px;
}

.stat-card {
    padding: 20px;
    border: 1px solid #ffffff;
    border-radius: 17px;
    background: #ffffffd9;
    box-shadow: 0 7px 24px #302b6710;
}

.stat-icon {
    font-size: 24px;
    margin-bottom: 9px;
}

.stat-number {
    font-size: 25px;
    font-weight: 800;
    color: var(--primary);
}

.stat-label {
    color: var(--muted);
    font-size: 13px;
    margin-top: 4px;
}

.panel {
    background: var(--surface);
    border: 1px solid #ffffff;
    border-radius: 20px;
    padding: 27px;
    margin-bottom: 24px;
    box-shadow: 0 8px 28px #302b670c;
}

.section-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 7px;
    font-size: 22px;
}

.heading-icon {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 13px;
    background: #eee9ff;
    font-size: 21px;
}

.section-subtitle {
    margin: 0 0 21px;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.6;
}

label {
    display: block;
    font-size: 13px;
    font-weight: 700;
    margin: 15px 0 7px;
    color: #454362;
}

input, textarea, select {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid #deddf0;
    border-radius: 11px;
    font: inherit;
    font-size: 14px;
    color: var(--ink);
    background: #fcfbff;
    transition: border-color .2s, box-shadow .2s;
}

input:focus, textarea:focus, select:focus {
    outline: none;
    border-color: #8b70fa;
    box-shadow: 0 0 0 4px #8b70fa20;
    background: white;
}

textarea {
    min-height: 85px;
    resize: vertical;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 18px;
}

.full-width { grid-column: 1 / -1; }

button, .button {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    gap: 7px;
    border: 0;
    border-radius: 10px;
    padding: 11px 17px;
    background: linear-gradient(120deg, #6348e8, #8756f3);
    color: white;
    cursor: pointer;
    text-decoration: none;
    font-size: 13px;
    font-weight: 700;
    font-family: inherit;
    transition: transform .2s, box-shadow .2s, opacity .2s;
}

button:hover, .button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px #6c4cf133;
}

.actions {
    display: flex;
    gap: 9px;
    margin-top: 20px;
    flex-wrap: wrap;
}

.secondary {
    background: #eeeaff;
    color: #5c43c9;
}

.delete {
    background: #fff0f1;
    color: #d9364f;
}

.search-row {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.search-row input { flex: 1; min-width: 0; }

.results-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
    margin: 22px 0 10px;
}

.results-count {
    color: var(--muted);
    font-size: 13px;
}

.question-card {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px;
    margin-top: 15px;
    background: linear-gradient(145deg, #fff, #fdfcff);
    transition: transform .2s, box-shadow .2s;
}

.question-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 9px 24px #40378b12;
}

.question-top {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: 17px;
}

.question-number {
    flex-shrink: 0;
    display: grid;
    place-items: center;
    width: 37px;
    height: 37px;
    border-radius: 12px;
    background: linear-gradient(135deg, #e9e4ff, #f5e7ff);
    color: #6243d5;
    font-weight: 800;
}

.question-card h3 {
    margin: 5px 0 0;
    line-height: 1.55;
    font-size: 17px;
    overflow-wrap: anywhere;
}

.options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.option {
    padding: 12px 13px;
    background: #f7f7fc;
    border: 1px solid #ececf5;
    border-radius: 10px;
    font-size: 13px;
    line-height: 1.55;
    overflow-wrap: anywhere;
}

.option strong {
    color: #6348e8;
    margin-right: 5px;
}

.correct {
    display: inline-block;
    margin: 15px 0 0;
    padding: 8px 12px;
    border-radius: 9px;
    color: #14754c;
    background: #e7f9ef;
    font-size: 12px;
    font-weight: 800;
}

.notice {
    padding: 14px 17px;
    border: 1px solid #bcebd0;
    border-radius: 12px;
    background: linear-gradient(120deg, #e6fbef, #f2fff7);
    color: #176c43;
    margin-bottom: 20px;
    font-size: 14px;
    font-weight: 600;
}

.empty-state {
    text-align: center;
    padding: 35px 15px;
    border: 1px dashed #dcd8f0;
    border-radius: 14px;
    background: #fcfbff;
}

.empty-icon { font-size: 38px; margin-bottom: 10px; }
.empty-state h3 { margin: 5px 0; }
.muted { color: var(--muted); font-size: 13px; line-height: 1.7; }

@media (max-width: 650px) {
    .container { padding: 15px 12px 35px; }
    header { padding: 25px 20px; border-radius: 18px; }
    .panel { padding: 19px; border-radius: 16px; }
    .stats { grid-template-columns: 1fr; gap: 10px; }
    .stat-card { display: flex; align-items: center; gap: 14px; padding: 14px; }
    .stat-icon { margin: 0; }
    .stat-number { font-size: 21px; }
    .form-grid, .options { grid-template-columns: 1fr; }
    .full-width { grid-column: auto; }
    .search-row { flex-wrap: wrap; }
    .search-row input { flex-basis: 100%; }
    .question-card { padding: 16px; }
}
</style>
"""


FORM_FIELDS = """
<div class="form-grid">
    <div class="full-width">
        <label for="question">📝 Question</label>
        <textarea id="question" name="question" placeholder="Enter your question here..." required>{{ q.question if q else '' }}</textarea>
    </div>

    <div>
        <label for="option-a">🅰️ Option A</label>
        <input id="option-a" name="a" placeholder="Enter option A" value="{{ q.a if q else '' }}" required>
    </div>

    <div>
        <label for="option-b">🅱️ Option B</label>
        <input id="option-b" name="b" placeholder="Enter option B" value="{{ q.b if q else '' }}" required>
    </div>

    <div>
        <label for="option-c">🆑 Option C</label>
        <input id="option-c" name="c" placeholder="Enter option C" value="{{ q.c if q else '' }}" required>
    </div>

    <div>
        <label for="option-d">🔠 Option D</label>
        <input id="option-d" name="d" placeholder="Enter option D" value="{{ q.d if q else '' }}" required>
    </div>

    <div class="full-width">
        <label for="answer">✅ Correct Answer</label>
        <select id="answer" name="answer" required>
            {% for option in ['A', 'B', 'C', 'D'] %}
            <option value="{{ option }}" {% if q and q.answer == option %}selected{% endif %}>
                Option {{ option }}
            </option>
            {% endfor %}
        </select>
    </div>
</div>
"""


EDIT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Edit Question | Quiz Question Bank</title>
""" + PAGE_STYLE + """
</head>
<body>
<div class="container">
    <header>
        <div class="brand">
            <div class="logo">✏️</div>
            <div>
                <h1>Edit Question</h1>
                <p>Update your question and answer options.</p>
            </div>
        </div>
        <span class="tagline">QUIZ QUESTION BANK · QUESTION EDITOR</span>
    </header>

    <div class="panel">
        <h2 class="section-heading"><span class="heading-icon">🛠️</span> Update Details</h2>
        <p class="section-subtitle">Make your changes below and save when ready.</p>
        <form method="POST">
            """ + FORM_FIELDS + """
            <div class="actions">
                <button type="submit">💾 Save Changes</button>
                <a class="button secondary" href="{{ url_for('home') }}">↩ Cancel</a>
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
<title>Quiz Question Bank | Dashboard</title>
""" + PAGE_STYLE + """
</head>
<body>
<div class="container">
    <header>
        <div class="brand">
            <div class="logo">🎓</div>
            <div>
                <h1>Quiz Question Bank</h1>
                <p>Version 3 — View Questions and Search</p>
            </div>
        </div>
        <span class="tagline">✨ V3 · VIEW QUESTIONS · SEARCH</span>
    </header>

    {% if message %}
    <div class="notice">🎉 {{ message }}</div>
    {% endif %}

    <div class="stats">
        <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div>
                <div class="stat-number">{{ total_questions }}</div>
                <div class="stat-label">Total Questions</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🔎</div>
            <div>
                <div class="stat-number">{{ questions|length }}</div>
                <div class="stat-label">Questions Showing</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🌈</div>
            <div>
                <div class="stat-number">A–D</div>
                <div class="stat-label">Multiple Choice</div>
            </div>
        </div>
    </div>

    <div class="panel">
        <h2 class="section-heading"><span class="heading-icon">✨</span> Add a New Question</h2>
        <p class="section-subtitle">Fill in the question, four options, and the correct answer.</p>

        <form method="POST" action="{{ url_for('add_question') }}">
            """ + FORM_FIELDS + """
            <div class="actions">
                <button type="submit">＋ Add Question</button>
            </div>
        </form>
    </div>

    <div class="panel">
        <h2 class="section-heading"><span class="heading-icon">🔍</span> Explore Questions</h2>
        <p class="section-subtitle">Search by question text or any of its answer options.</p>

        <form method="GET" action="{{ url_for('home') }}">
            <div class="search-row">
                <input type="search" name="q"
                       placeholder="Type a keyword to search..."
                       value="{{ search_query }}" aria-label="Search questions">
                <button type="submit">🔎 Search</button>
                {% if search_query %}
                <a class="button secondary" href="{{ url_for('home') }}">✕ Clear</a>
                {% endif %}
            </div>
        </form>

        <div class="results-bar">
            <strong>🗂️ Question Library</strong>
            <span class="results-count">
                Showing {{ questions|length }} of {{ total_questions }} question(s)
                {% if search_query %} for "{{ search_query }}"{% endif %}
            </span>
        </div>

        {% for item in questions %}
        <div class="question-card">
            <div class="question-top">
                <div class="question-number">Q{{ loop.index }}</div>
                <h3>{{ item.question }}</h3>
            </div>

            <div class="options">
                <div class="option"><strong>A.</strong> {{ item.a }}</div>
                <div class="option"><strong>B.</strong> {{ item.b }}</div>
                <div class="option"><strong>C.</strong> {{ item.c }}</div>
                <div class="option"><strong>D.</strong> {{ item.d }}</div>
            </div>

            <p class="correct">✓ Correct Answer: {{ item.answer }}</p>

            <div class="actions">
                <a class="button" href="{{ url_for('edit_question', question_id=item.id) }}">✏️ Edit</a>
                <form method="POST"
                      action="{{ url_for('delete_question', question_id=item.id) }}"
                      onsubmit="return confirm('Delete this question permanently?');">
                    <button class="delete" type="submit">🗑️ Delete</button>
                </form>
            </div>
        </div>
        {% else %}
        <div class="empty-state">
            <div class="empty-icon">📭</div>
            <h3>No questions found</h3>
            <p class="muted">Try a different keyword or add your first question using the form above.</p>
        </div>
        {% endfor %}
    </div>

    <p class="muted" style="text-align:center">🎓 Quiz Question Bank · Built with Flask and SQLite</p>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    search_query = request.args.get("q", "").strip()

    with get_db_connection() as conn:
        total_questions = conn.execute(
            "SELECT COUNT(*) FROM questions"
        ).fetchone()[0]

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
        total_questions=total_questions,
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
    app.run(host="0.0.0.0", port=5000, debug=False)