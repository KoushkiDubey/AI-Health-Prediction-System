
import sqlite3

DB_NAME = "health_records.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT NOT NULL,
            glucose REAL NOT NULL,
            haemoglobin REAL NOT NULL,
            cholesterol REAL NOT NULL,
            remarks TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


def add_patient(full_name, dob, email, glucose,
                haemoglobin, cholesterol, remarks=""):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients
        (full_name, dob, email, glucose, haemoglobin,
         cholesterol, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, dob, email, glucose,
          haemoglobin, cholesterol, remarks))

    conn.commit()
    conn.close()


def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients ORDER BY id")

    records = cursor.fetchall()
    conn.close()

    return records


def get_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    )

    record = cursor.fetchone()
    conn.close()

    return record


def update_patient(patient_id, full_name, dob, email,
                   glucose, haemoglobin, cholesterol, remarks):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE patients
        SET full_name = ?, dob = ?, email = ?,
            glucose = ?, haemoglobin = ?,
            cholesterol = ?, remarks = ?
        WHERE id = ?
    """, (full_name, dob, email, glucose,
          haemoglobin, cholesterol, remarks, patient_id))

    conn.commit()
    conn.close()


def delete_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE id = ?",
        (patient_id,)
    )

    conn.commit()
    conn.close()
