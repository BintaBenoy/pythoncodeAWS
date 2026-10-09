
from flask import Flask, request, render_template_string, redirect, url_for
import pymysql
import db_config

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS Student Registration</title>
    <style>
        body { font-family: Arial; max-width: 700px; margin: 40px auto; padding: 20px; }
        input, button { padding: 10px; margin: 6px 0; }
        input { width: 95%; }
        button { background: #1769aa; color: white; border: 0; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>AWS Student Registration</h1>
    <p>Flask + EC2 + RDS MySQL</p>

    <form method="post" action="/add">
        <input name="name" placeholder="Student name" required>
        <input name="email" type="email" placeholder="Email address">
        <button type="submit">Register Student</button>
    </form>

    {% if message %}<p>{{ message }}</p>{% endif %}

    <h2>Registered Students</h2>
    <table>
        <tr><th>ID</th><th>Name</th><th>Email</th></tr>
        {% for s in students %}
        <tr>
            <td>{{ s.id }}</td>
            <td>{{ s.name }}</td>
            <td>{{ s.email or '' }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def get_connection():
    return pymysql.connect(
        host=db_config.DB_HOST,
        user=db_config.DB_USER,
        password=db_config.DB_PASSWORD,
        database=db_config.DB_NAME,
        port=db_config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

@app.route("/")
def index():
    message = request.args.get("message", "")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, email FROM students ORDER BY id DESC"
                )
                students = cur.fetchall()
        return render_template_string(
            PAGE, students=students, message=message
        )
    except Exception:
        app.logger.exception("Database operation failed")
        return "Database connection failed. Check server logs.", 500

@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip() or None

    if not name:
        return "Student name is required.", 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO students (name, email) VALUES (%s, %s)",
                    (name, email)
                )
            conn.commit()

        return redirect(url_for("index", message="Student registered!"))
    except Exception:
        app.logger.exception("Student registration failed")
        return "Could not save the student. Check server logs.", 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
