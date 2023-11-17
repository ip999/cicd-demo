import requests
#import sqlite3
import psycopg2
import json
from datetime import datetime
import logging
import sys
import os


# Logging setup
# logging.basicConfig(filename='app.log', level=logging.INFO, 
#                     format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(stream=sys.stdout, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info('Script started running.')
logging.info(os.environ["DATABASE_URL"])


# Constants
URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
#DATABASE = "kev_monitor.db"

# Database initialization


def init_db():
    #conn = sqlite3.connect(DATABASE)
    conn = psycopg2.connect(os.environ["DATABASE_URL"])

    cur = conn.cursor()

    # Main Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Main (
            MainID SERIAL PRIMARY KEY,
            CatalogVersion TEXT,
            DateReleased TEXT,
            Count INTEGER,
            JSONContent TEXT
        )
    """)

    # Vulnerabilities Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Vulnerabilities (
            VulnerabilityID SERIAL PRIMARY KEY,
            MainID INTEGER REFERENCES Main(MainID),
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
            ChangeID SERIAL PRIMARY KEY,
            VulnerabilityID INTEGER REFERENCES Vulnerabilities(VulnerabilityID),
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
    conn = psycopg2.connect(os.environ["DATABASE_URL"])

    cur = conn.cursor()

    logging.info("Preparing to insert data...")
    logging.info(f"CatalogVersion: {data['catalogVersion']}")
    logging.info(f"DateReleased: {data['dateReleased']}")
    logging.info(f"Count: {data['count']}")
    logging.info(f"JSONContent: {len(json.dumps(data))}")


    # Insert main data
    cur.execute("""
        INSERT INTO Main (CatalogVersion, DateReleased, Count, JSONContent) VALUES (%s, %s, %s, %s)
    """, (data['catalogVersion'], data['dateReleased'], data['count'], json.dumps(data)))




    main_id = cur.lastrowid

    # Process vulnerabilities
    for vuln in data['vulnerabilities']:
        cve_id = vuln['cveID']
        cur.execute("SELECT * FROM Vulnerabilities WHERE CVEID = %s", (cve_id,))
        existing_vuln = cur.fetchone()

        # If vulnerability exists, detect changes
        if existing_vuln:
            for key, value in vuln.items():
                # +2 to skip the initial columns (ID and MainID)
                if str(existing_vuln[list(vuln.keys()).index(key) + 2]) != str(value):
                    cur.execute("""
                        INSERT INTO Changes (VulnerabilityID, ChangedDate, ChangedKey, OldValue, NewValue) VALUES (%s, %s, %s, %s, %s)
                    """, (existing_vuln[0], datetime.now(), key, existing_vuln[vuln.keys().index(key) + 2], value))
                    logging.info(f"Change detected for CVEID {cve_id}. Key: {key}. Old value: {existing_vuln[vuln.keys().index(key) + 2]}. New value: {value}.")

            # Update the existing record
            columns = ", ".join([f"{k} = ?" for k in vuln.keys()])
            cur.execute(f"UPDATE Vulnerabilities SET {columns} WHERE CVEID = ?", list(
                vuln.values()) + [cve_id])

        # If new vulnerability, insert it
        else:
            columns = ", ".join(vuln.keys())
            placeholders = ", ".join(["%s" for _ in vuln.values()])
            cur.execute(f"""
                INSERT INTO Vulnerabilities (MainID, {columns}, DateStored) VALUES (%s, {placeholders}, %s)
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