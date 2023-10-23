import requests
import sqlite3
import json
from datetime import datetime
import logging
import sys



# Logging setup
# logging.basicConfig(filename='app.log', level=logging.INFO, 
#                     format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(stream=sys.stdout, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info('Script started running.')


# Constants
URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
DATABASE = "kev_monitor.db"

# Database initialization


def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Main Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Main (
            MainID INTEGER PRIMARY KEY,
            CatalogVersion TEXT,
            DateReleased TEXT,
            Count INTEGER,
            JSONContent TEXT
        )
    """)

    # Vulnerabilities Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Vulnerabilities (
            VulnerabilityID INTEGER PRIMARY KEY,
            MainID INTEGER,
            CVEID TEXT UNIQUE,
            VendorProject TEXT,
            Product TEXT,
            VulnerabilityName TEXT,
            DateAdded TEXT,
            ShortDescription TEXT,
            RequiredAction TEXT,
            DueDate TEXT,
            KnownRansomwareCampaignUse TEXT,
            Notes TEXT,
            DateStored TEXT
        )
    """)

    # Changes Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Changes (
            ChangeID INTEGER PRIMARY KEY,
            VulnerabilityID INTEGER,
            ChangedDate TEXT,
            ChangedKey TEXT,
            OldValue TEXT,
            NewValue TEXT
        )
    """)

    conn.commit()
    conn.close()

# Fetch the JSON data


def fetch_data():
    logging.info("Fetching data")
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Failed to fetch data. HTTP Status Code: {response.status_code}")
        return None

# Store and detect changes


def process_data(data):
    logging.info("Processing data...")
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Insert main data
    cur.execute("""
        INSERT INTO Main (CatalogVersion, DateReleased, Count, JSONContent) VALUES (?, ?, ?, ?)
    """, (data['catalogVersion'], data['dateReleased'], data['count'], json.dumps(data)))
    main_id = cur.lastrowid

    # Process vulnerabilities
    for vuln in data['vulnerabilities']:
        cve_id = vuln['cveID']
        existing_vuln = cur.execute(
            "SELECT * FROM Vulnerabilities WHERE CVEID = ?", (cve_id,)).fetchone()

        # If vulnerability exists, detect changes
        if existing_vuln:
            for key, value in vuln.items():
                # +2 to skip the initial columns (ID and MainID)
                if str(existing_vuln[list(vuln.keys()).index(key) + 2]) != str(value):
                    cur.execute("""
                        INSERT INTO Changes (VulnerabilityID, ChangedDate, ChangedKey, OldValue, NewValue) VALUES (?, ?, ?, ?, ?)
                    """, (existing_vuln[0], datetime.now(), key, existing_vuln[vuln.keys().index(key) + 2], value))
                    logging.info(f"Change detected for CVEID {cve_id}. Key: {key}. Old value: {existing_vuln[vuln.keys().index(key) + 2]}. New value: {value}.")

            # Update the existing record
            columns = ", ".join([f"{k} = ?" for k in vuln.keys()])
            cur.execute(f"UPDATE Vulnerabilities SET {columns} WHERE CVEID = ?", list(
                vuln.values()) + [cve_id])

        # If new vulnerability, insert it
        else:
            columns = ", ".join(vuln.keys())
            placeholders = ", ".join(["?" for _ in vuln.values()])
            cur.execute(f"""
                INSERT INTO Vulnerabilities (MainID, {columns}, DateStored) VALUES (?, {placeholders}, ?)
            """, [main_id] + list(vuln.values()) + [datetime.now()])

    conn.commit()
    conn.close()


def update_data_from_source():
    init_db()
    data = fetch_data()
    if data:
        process_data(data)

if __name__ == "__main__":
    update_data_from_source()