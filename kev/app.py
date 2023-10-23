from flask import Flask, render_template, jsonify
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from main import update_data_from_source
import os
import time

app = Flask(__name__)
DATABASE = "kev_monitor.db"


@app.route('/')
def index():
    # Fetch all vulnerabilities
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    vulnerabilities = cur.execute("SELECT * FROM Vulnerabilities ORDER BY DateAdded DESC").fetchall()
    conn.close()

    return render_template('index.html', vulnerabilities=vulnerabilities)

@app.route('/version')
def version():
    app_filepath = os.path.abspath(__file__)
    db_filepath = os.path.join(os.path.dirname(app_filepath), 'kev_monitor.db')
    app_timestamp = os.path.getmtime(app_filepath)
    app_readable_time = time.ctime(app_timestamp)
    db_timestamp = os.path.getmtime(db_filepath)
    db_readable_time = time.ctime(db_timestamp)

    return jsonify({
        'app.py': {'last_modified_at': app_readable_time},
        'db.db': {'last_modified_at': db_readable_time}
    })

@app.route('/vulnerability/<cve_id>')
def vulnerability(cve_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Fetch specific vulnerability by CVEID
    vuln = cur.execute(
        "SELECT * FROM Vulnerabilities WHERE CVEID = ?", (cve_id,)).fetchone()

    # Fetch changes for the given vulnerability
    changes = cur.execute(
        "SELECT * FROM Changes WHERE VulnerabilityID = ?", (vuln[0],)).fetchall()
    conn.close()

    return render_template('vulnerability.html', vuln=vuln, changes=changes)


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_data_from_source, 'interval', hours=24)
    scheduler.start()
    
    app.run(debug=True, port=5001)
