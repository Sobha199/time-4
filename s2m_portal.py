
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

form_headers = [
    "Date", "Emp ID", "Emp Name", "Project", "Project Category", 
    "Login ID", "Login Name", "Team Lead Name", "Chart ID", "Page No", 
    "No of DOS", "No of Codes", "Error Type", "Error Comments", 
    "No of Errors", "Chart Status", "Auditor Emp ID", "Auditor Emp Name"
]

# Load login credentials and logo
login_df = pd.read_csv("login_coder.csv")
logo = Image.open("s2m-logo.png")

# Setup session logs path
SESSION_LOG_PATH = "session_logs.csv"

# Page config
st.set_page_config(page_title="S2M Portal", layout="centered")

# Session state init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.emp_id = ""
    st.session_state.emp_name = ""
    st.session_state.team_lead = ""
    st.session_state.login_time = None

def log_session_start(emp_id):
    now = datetime.now()
    st.session_state.login_time = now
    return now

def log_session_end():
    if st.session_state.login_time:
        logout_time = datetime.now()
        duration = (logout_time - st.session_state.login_time).total_seconds() / 3600  # hours
        df = pd.DataFrame([{
            "Emp ID": st.session_state.emp_id,
            "Emp Name": st.session_state.emp_name,
            "Login Time": st.session_state.login_time,
            "Logout Time": logout_time,
            "Hours": round(duration, 2)
        }])
        if os.path.exists(SESSION_LOG_PATH):
            df.to_csv(SESSION_LOG_PATH, mode="a", header=False, index=False)
        else:
            df.to_csv(SESSION_LOG_PATH, index=False)

def login_page():
    st.image(logo, width=200)
    st.markdown("<h2 style='color:skyblue;'>S2M Login Portal</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Username", key="user")
        password = st.text_input("Password", type="password", key="pass")
        submitted = st.form_submit_button("Sign In")
        if submitted:
            match = login_df[(login_df["Emp ID"].astype(str) == username) & (login_df["Password"] == password)]
            if not match.empty:
                st.success("Login Successful")
                st.session_state.authenticated = True
                st.session_state.emp_id = username
                st.session_state.emp_name = match.iloc[0]["Emp Name"]
                st.session_state.team_lead = match.iloc[0]["Team Lead"]
                log_session_start(username)
            else:
                st.error("Invalid credentials")

def form_page():
    st.image(logo, width=150)
    st.markdown("<h2 style='color:skyblue;'>Form Entry</h2>", unsafe_allow_html=True)
    with st.form("entry_form"):
        today = datetime.now().strftime("%Y-%m-%d")
        emp_id = st.session_state.emp_id
        emp_name = st.session_state.emp_name
        team_lead = st.session_state.team_lead

        st.write("Emp ID:", emp_id)
        st.write("Emp Name:", emp_name)
        st.write("Team Lead Name:", team_lead)

        project = st.selectbox("Project", ["Elevance MA", "Elevance ACA", "Health OS"])
        category = st.selectbox("Project Category", ["Entry", "Recheck", "QA"])
        login_names = login_df["Login Name"].unique().tolist()
        login_name = st.selectbox("Login Name", login_names)
        login_id = login_df[login_df["Login Name"] == login_name]["Login ID"].values[0]

        chart_id = st.text_input("Chart ID")
        page_no = st.text_input("Page No")
        dos = st.text_input("No of DOS")
        codes = st.text_input("No of Codes")
        error_type = st.text_input("Error Type")
        error_comments = st.text_input("Error Comments")
        no_of_errors = st.text_input("No of Errors")
        chart_status = st.text_input("Chart Status")
        auditor_emp_id = st.text_input("Auditor Emp ID")
        auditor_emp_name = st.text_input("Auditor Emp Name")

        submit = st.form_submit_button("Submit")
        if submit:
            new_data = pd.DataFrame([[
                today, emp_id, emp_name, project, category,
                login_id, login_name, team_lead, chart_id, page_no,
                dos, codes, error_type, error_comments,
                no_of_errors, chart_status, auditor_emp_id, auditor_emp_name
            ]], columns=form_headers)
            new_data.to_csv("data.csv", mode="a", header=not os.path.exists("data.csv"), index=False)
            st.success("Data submitted successfully!")

def dashboard_page():
    st.image(logo, width=150)
    st.markdown("<h2 style='color:skyblue;'>Dashboard</h2>", unsafe_allow_html=True)
    try:
        df = pd.read_csv("data.csv")
        charts = len(df)
        dos = df["No of DOS"].astype(str).apply(pd.to_numeric, errors='coerce').sum()
        icd = df["No of Codes"].astype(str).apply(pd.to_numeric, errors='coerce').sum()
        working_days = df["Date"].nunique()
        cph = round(charts / working_days, 2) if working_days else 0

        st.metric("Working Days", working_days)
        st.metric("Charts", charts)
        st.metric("No of DOS", int(dos))
        st.metric("No of ICD", int(icd))
        st.metric("CPH", cph)
    except:
        st.warning("No data submitted yet.")

    st.markdown("---")
    st.markdown("### Login Tracking")
    if os.path.exists(SESSION_LOG_PATH):
        logs = pd.read_csv(SESSION_LOG_PATH)
        user_logs = logs[logs["Emp ID"] == st.session_state.emp_id]
        total_logins = len(user_logs)
        total_hours = round(user_logs["Hours"].sum(), 2)
        st.metric("Total Logins", total_logins)
        st.metric("Total Hours Logged In", total_hours)
    else:
        st.info("No login data available.")

# App Flow
if not st.session_state.authenticated:
    login_page()
else:
    page = st.sidebar.radio("Navigate", ["Form", "Dashboard", "Logout"])
    if page == "Form":
        form_page()
    elif page == "Dashboard":
        dashboard_page()
    elif page == "Logout":
        log_session_end()
        st.session_state.authenticated = False
        st.session_state.emp_id = ""
        st.session_state.emp_name = ""
        st.session_state.team_lead = ""
        st.session_state.login_time = None
        st.success("Logged out successfully.")
