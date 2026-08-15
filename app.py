from flask import Flask, render_template, request, redirect
from datetime import datetime
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL environment variable is missing")

    return psycopg2.connect(database_url)

# Create the table if it doesn't exist
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    application_name TEXT,
    severity TEXT,
    status TEXT,
    created_on TEXT    
)
""")

conn.commit()
conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/save", methods=["POST"])
def save():
    incident_id = request.form["incident_id"].upper()
    application_name = request.form["application_name"]
    severity = request.form["severity"]
    status = request.form["status"]
    created_on = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    print("Incident ID:", incident_id)
    print("Application:", application_name)
    print("Severity:", severity)
    print("Status:", status)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO incidents (
            incident_id,
            application_name,
            severity,
            status,
            created_on
        )
        VALUES (%s, %s, %s, %s, %s)
        """, (
            incident_id,
            application_name,
            severity,
            status,
            created_on
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        return "Incident ID already exists!"

    finally:
        conn.close()

    return redirect("/view")

@app.route("/search", methods=["POST"])
def search():

    incident_id = request.form["incident_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM incidents
    WHERE incident_id = %s
    """, (incident_id,))

    incidents = cursor.fetchall()

    conn.close()

    return render_template("view.html", incidents=incidents)


@app.route("/view")
def view():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT incident_id,
           application_name,
           severity,
           status,
           created_on
    FROM incidents
    """)
    incidents = cursor.fetchall()

    conn.close()

    return render_template("view.html", incidents=incidents)

@app.route("/delete/<incident_id>")
def delete(incident_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM incidents WHERE incident_id = %s",
        (incident_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/view")

@app.route("/edit/<incident_id>")
def edit(incident_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM incidents WHERE incident_id = %s",
        (incident_id,)
    )

    incident = cursor.fetchone()

    conn.close()

    return render_template("edit.html", incident=incident)

@app.route("/update", methods=["POST"])
def update():

    incident_id = request.form["incident_id"]
    application_name = request.form["application_name"]
    severity = request.form["severity"]
    status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE incidents
        SET application_name = %s,
            severity = %s,
            status = %s
        WHERE incident_id = %s
    """, (
        application_name,
        severity,
        status,
        incident_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/view")

if __name__ == "__main__":
    app.run(debug=True)