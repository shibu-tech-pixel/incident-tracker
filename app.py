from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import os

app = Flask(__name__)

# Create the table if it doesn't exist
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    application_name TEXT,
    severity TEXT,
    status TEXT,
    created_on TEXT,
    last_updated TEXT 
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
    created_on = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%b-%Y %I:%M %p")
    last_updated = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%b-%Y %I:%M %p")
    print("Incident ID:", incident_id)
    print("Application:", application_name)
    print("Severity:", severity)
    print("Status:", status)

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO incidents (
            incident_id,
            application_name,
            severity,
            status,
            created_on,
            last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            application_name,
            severity,
            status,
            created_on,
            last_updated
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

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM incidents
    WHERE incident_id = ?
    """, (incident_id,))

    incidents = cursor.fetchall()

    conn.close()

    return render_template("view.html", incidents=incidents)


@app.route("/view")
def view():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Fetch all incidents
    cursor.execute("""
    SELECT incident_id,
           application_name,
           severity,
           status,
           created_on,
           last_updated
    FROM incidents
    """)
    incidents = cursor.fetchall()

    # Dashboard Counts
    cursor.execute("SELECT COUNT(*) FROM incidents")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE status='Open'")
    open_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE status='Resolved'")
    resolved_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE severity='High'")
    high_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "view.html",
        incidents=incidents,
        total=total,
        open_count=open_count,
        resolved_count=resolved_count,
        high_count=high_count
    )


@app.route("/delete/<incident_id>")
def delete(incident_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM incidents WHERE incident_id = ?",
        (incident_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view")

@app.route("/edit/<incident_id>")
def edit(incident_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM incidents WHERE incident_id = ?",
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
    last_updated = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
UPDATE incidents
SET application_name = ?,
    severity = ?,
    status = ?,
    last_updated = ?
WHERE incident_id = ?
""", (
    application_name,
    severity,
    status,
    last_updated,
    incident_id
))

    conn.commit()
    conn.close()

    return redirect("/view")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)