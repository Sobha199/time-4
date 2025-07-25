
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# Page config
st.set_page_config(page_title="S2M Coder Portal", layout="wide")

# Load logo
logo = Image.open("s2m-logo.png")
st.image(logo, width=150)

# Load login data
login_df = pd.read_csv("login coder.csv")

def log_session_start(username):
    st.session_state["login_time"] = datetime.now()
    st.session_state["login_user"] = username

def login_page():
    st.title("Login Portal")
    username = st.text_input("Login ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in login_df["Login ID"].values:
            stored_password = login_df.loc[login_df["Login ID"] == username, "Password"].values[0]
            if password == stored_password:
                log_session_start(username)  # ✅ this won't error now
                st.session_state.logged_in = True
                st.session_state.emp_id = login_df.loc[login_df["Login ID"] == username, "Emp ID"].values[0]
                st.session_state.emp_name = login_df.loc[login_df["Login ID"] == username, "Emp Name"].values[0]
                st.success("Login successful")
                st.experimental_rerun()
            else:
                st.error("Incorrect password")
        else:
            st.error("Login ID not found")

# Form page
def form_page():
    st.title("Chart Submission Form")
    emp_id = st.session_state.emp_id
    emp_name = st.session_state.emp_name
    date = st.date_input("Date", datetime.today())
    project = st.selectbox("Project", ["Project A", "Project B", "Project C"])
    pages_completed = st.number_input("Pages Completed", min_value=0, step=1)
    charts = st.number_input("Charts Completed", min_value=0, step=1)
    icd = st.number_input("ICD Coded", min_value=0, step=1)
    submit = st.button("Submit")
    if submit:
        df = pd.DataFrame([{
            "Date": date,
            "Emp ID": emp_id,
            "Emp Name": emp_name,
            "Project": project,
            "Pages": pages_completed,
            "Charts": charts,
            "ICD": icd
        }])
        output_file = "chart_tracking.xlsx"
        if os.path.exists(output_file):
            existing_df = pd.read_excel(output_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        df.to_excel(output_file, index=False)
        st.success("Submitted successfully")
        st.experimental_rerun()

# Logout and dashboard
def dashboard_page():
    st.title("Dashboard")
    logout = st.button("Logout")
    if logout:
        log_session_end()
        st.session_state.logged_in = False
        st.experimental_rerun()

    # Show submitted chart data
    output_file = "chart_tracking.xlsx"
    if os.path.exists(output_file):
        df = pd.read_excel(output_file)
        st.dataframe(df)
        st.download_button(
            label="Download Submitted Charts",
            data=df.to_excel(index=False, engine='openpyxl'),
            file_name="submitted_charts.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Log session
def log_session_end():
    logout_time = datetime.now()
    login_time = st.session_state.login_time
    duration = (logout_time - login_time).total_seconds() / 3600
    df = pd.DataFrame([{
        "Emp ID": st.session_state.emp_id,
        "Emp Name": st.session_state.emp_name,
        "Login Time": login_time.strftime("%H:%M:%S"),
        "Logout Time": logout_time.strftime("%H:%M:%S"),
        "Hours": round(duration, 2)
    }])
    if os.path.exists(session_log_file):
        existing = pd.read_csv(session_log_file)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(session_log_file, index=False)

# Routing
if not st.session_state.logged_in:
    login_page()
else:
    tab1, tab2 = st.tabs(["Submit Form", "Dashboard"])
    with tab1:
        form_page()
    with tab2:
        dashboard_page()
