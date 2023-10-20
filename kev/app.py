from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
DATABASE = "kev_monitor.db"


@app.route('/')
def index():
    # Fetch all vulnerabilities
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    vulnerabilities = cur.execute("SELECT * FROM Vulnerabilities").fetchall()
    conn.close()

    return render_template('index.html', vulnerabilities=vulnerabilities)


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
    app.run(debug=True, port=5001)
