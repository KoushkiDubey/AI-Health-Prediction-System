
import re
from datetime import datetime, date

import pandas as pd
import streamlit as st

from database import (
    initialize_database,
    add_patient,
    get_all_patients,
    get_patient,
    update_patient,
    delete_patient
)

from health_ai import generate_health_remarks


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Health Prediction System",
    page_icon="🏥",
    layout="wide"
)

initialize_database()


# ---------------- VALIDATION FUNCTIONS ----------------

def validate_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email.strip()) is not None


def validate_dob(dob):
    try:
        parsed_date = datetime.strptime(
            dob.strip().replace(".", "/"),
            "%d/%m/%Y"
        ).date()

        if parsed_date > date.today():
            return None, "Date of birth cannot be in the future."

        return parsed_date, None

    except ValueError:
        return None, "Enter a valid date in DD/MM/YYYY format."


def validate_blood_values(glucose, haemoglobin, cholesterol):
    try:
        values = [
            float(glucose),
            float(haemoglobin),
            float(cholesterol)
        ]

        if any(value <= 0 for value in values):
            return None, "Blood test values must be greater than zero."

        return values, None

    except (ValueError, TypeError):
        return None, "Blood test values must be numeric."


def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


# ---------------- HELPER FUNCTIONS ----------------

def generate_remarks(glucose, haemoglobin, cholesterol):
    api_key = get_api_key()

    if not api_key:
        return "AI service unavailable: API key not configured."

    return generate_health_remarks(
        glucose,
        haemoglobin,
        cholesterol,
        api_key
    )



def format_records(records):
    columns = [
        "Database ID", "Full Name", "Date of Birth", "Email",
        "Glucose", "Haemoglobin", "Cholesterol", "Remarks"
    ]

    df = pd.DataFrame(records, columns=columns)

    df.insert(0, "Sr. No.", range(1, len(df) + 1))

    if not df.empty:
        df["Date of Birth"] = pd.to_datetime(
            df["Date of Birth"]
        ).dt.strftime("%d/%m/%Y")

    return df



# ---------------- APPLICATION HEADER ----------------

st.title("🏥 AI Health Prediction System")

st.caption(
    "Patient Management | Blood Test Analysis | AI-Generated Remarks"
)

st.info(
    "This application provides informational health-risk summaries "
    "and is not a substitute for professional medical advice."
)

# ---------------- NAVIGATION ----------------

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Patient", "Patient Records"]
)


# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    records = get_all_patients()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Patient Records", len(records))

    with col2:
        st.metric(
            "AI Integration",
            "Configured" if get_api_key() else "Not Configured"
        )

    st.subheader("Welcome")

    st.write(
        "Use the navigation menu to add patient information, "
        "view existing records, update details or delete records."
    )

    if records:
        st.subheader("Recent Patient Records")
        st.dataframe(
            format_records(records).tail(5),
            use_container_width=True,
            hide_index=True
        )


# ---------------- ADD PATIENT ----------------

elif menu == "Add Patient":

    st.subheader("Add New Patient")

    with st.form("add_patient_form"):

        full_name = st.text_input("Full Name")

        dob = st.text_input(
            "Date of Birth (DD/MM/YYYY)",
            placeholder="28/01/1960"
        )

        email = st.text_input("Email Address")

        col1, col2, col3 = st.columns(3)

        with col1:
            glucose = st.text_input("Glucose")

        with col2:
            haemoglobin = st.text_input("Haemoglobin")

        with col3:
            cholesterol = st.text_input("Cholesterol")

        submitted = st.form_submit_button(
            "Generate Remarks & Save Patient",
            use_container_width=True
        )

        if submitted:

            errors = []

            if not full_name.strip():
                errors.append("Full name is required.")

            parsed_dob, dob_error = validate_dob(dob)

            if dob_error:
                errors.append(dob_error)

            if not validate_email(email):
                errors.append("Please enter a valid email address.")

            blood_values, blood_error = validate_blood_values(
                glucose, haemoglobin, cholesterol
            )

            if blood_error:
                errors.append(blood_error)

            if errors:
                for error in errors:
                    st.error(error)

            else:
                g, h, c = blood_values

                with st.spinner("Generating AI health remarks..."):
                    remarks = generate_remarks(g, h, c)

                add_patient(
                    full_name.strip(),
                    parsed_dob.isoformat(),
                    email.strip(),
                    g, h, c,
                    remarks
                )

                st.success("Patient record saved successfully!")

                st.subheader("AI-Generated Remarks")
                st.write(remarks)


# ---------------- PATIENT RECORDS ----------------

elif menu == "Patient Records":

    st.subheader("Patient Records")

    records = get_all_patients()

    if not records:
        st.info("No patient records available.")

    else:

        st.dataframe(
            format_records(records),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ---------------- UPDATE PATIENT ----------------

        st.subheader("Edit Patient")

        patient_options = {
            f"{record[0]} - {record[1]}": record[0]
            for record in records
        }

        selected_patient = st.selectbox(
            "Select patient to edit",
            list(patient_options.keys()),
            key="edit_patient"
        )

        patient_id = patient_options[selected_patient]
        patient = get_patient(patient_id)

        with st.form("edit_patient_form"):

            name = st.text_input(
                "Full Name",
                value=patient[1],
                key="edit_name"
            )

            dob_value = datetime.strptime(
                patient[2], "%Y-%m-%d"
            ).strftime("%d/%m/%Y")

            dob = st.text_input(
                "Date of Birth",
                value=dob_value,
                key="edit_dob"
            )

            email = st.text_input(
                "Email Address",
                value=patient[3],
                key="edit_email"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                glucose = st.text_input(
                    "Glucose",
                    value=str(patient[4]),
                    key="edit_glucose"
                )

            with col2:
                haemoglobin = st.text_input(
                    "Haemoglobin",
                    value=str(patient[5]),
                    key="edit_haemoglobin"
                )

            with col3:
                cholesterol = st.text_input(
                    "Cholesterol",
                    value=str(patient[6]),
                    key="edit_cholesterol"
                )

            update_button = st.form_submit_button("Update Patient")

            if update_button:

                errors = []

                if not name.strip():
                    errors.append("Full name is required.")

                parsed_dob, dob_error = validate_dob(dob)

                if dob_error:
                    errors.append(dob_error)

                if not validate_email(email):
                    errors.append("Please enter a valid email address.")

                blood_values, blood_error = validate_blood_values(
                    glucose, haemoglobin, cholesterol
                )

                if blood_error:
                    errors.append(blood_error)

                if errors:
                    for error in errors:
                        st.error(error)

                else:
                    g, h, c = blood_values

                    with st.spinner("Updating AI remarks..."):
                        remarks = generate_remarks(g, h, c)

                    update_patient(
                        patient_id,
                        name.strip(),
                        parsed_dob.isoformat(),
                        email.strip(),
                        g, h, c,
                        remarks
                    )

                    st.success("Patient updated successfully!")
                    st.rerun()

        st.divider()

        # ---------------- DELETE PATIENT ----------------

        st.subheader("Delete Patient")

        delete_selection = st.selectbox(
            "Select patient to delete",
            list(patient_options.keys()),
            key="delete_patient"
        )

        if st.button("Delete Selected Patient", type="primary"):

            delete_id = patient_options[delete_selection]

            delete_patient(delete_id)

            st.success("Patient deleted successfully!")
            st.rerun()
