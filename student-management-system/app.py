
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


# Connect to the database
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create the students table
def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            marks REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Display all students and search results
@app.route("/")
def home():
    search = request.args.get("search", "").strip()

    connection = get_db_connection()

    students = connection.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
           OR email LIKE ?
           OR course LIKE ?
        ORDER BY id DESC
    """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()

    connection.close()

    return render_template(
        "index.html",
        students=students,
        search=search
    )


# Add a new student
@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    course = request.form.get("course", "").strip()
    marks_text = request.form.get("marks", "").strip()

    if not name or not email or not course or not marks_text:
        return "All fields are required.", 400

    try:
        marks = float(marks_text)
        if not 0 <= marks <= 100:
            return "Marks must be between 0 and 100.", 400
    except ValueError:
        return "Marks must be a valid number.", 400

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO students (name, email, course, marks)
        VALUES (?, ?, ?, ?)
    """, (name, email, course, marks))

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


# Edit an existing student
@app.route("/edit/<int:student_id>", methods=["POST"])
def edit_student(student_id):
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    course = request.form.get("course", "").strip()
    marks_text = request.form.get("marks", "").strip()

    if not name or not email or not course or not marks_text:
        return "All fields are required.", 400

    try:
        marks = float(marks_text)
        if not 0 <= marks <= 100:
            return "Marks must be between 0 and 100.", 400
    except ValueError:
        return "Marks must be a valid number.", 400

    connection = get_db_connection()

    connection.execute("""
        UPDATE students
        SET name = ?, email = ?, course = ?, marks = ?
        WHERE id = ?
    """, (name, email, course, marks, student_id))

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


# Delete a student
@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
