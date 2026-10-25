from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "tasks.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    completed_count = sum(task["completed"] for task in tasks)
    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        completed_count=completed_count
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("task", "").strip()

    if title:
        conn = get_db_connection()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()

    return redirect(url_for("home"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete(task_id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE tasks
        SET completed = CASE WHEN completed = 0 THEN 1 ELSE 0 END
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
