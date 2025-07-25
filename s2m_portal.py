
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from PIL import Image

st.set_page_config(page_title="S2M Coder Portal", layout="wide")

# Constants
LOGO_PATH = "s2m-logo.png"
DATA_FILE = "data.csv"
LOGIN_CSV = "login coder.csv"
SESSION_LOG_PATH = "login_sessions.csv"

# Load logo
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)

# Session management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "login_time" not in st.session_state:
    st.session_state.login_time = None

# Login function
def login(username, password):
    if os.path.exists(LOGIN_CSV):
        df = pd.read_csv(LOGIN_CSV)
        user = df[(df["UserName"] == username) & (df["Password"] == password)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.login_time = datetime.now()
            return user.iloc[0]
    return None

# Logout function with logging
def logout():
    if st.session_state.logged_in:
        logout_time = datetime.now()
        login_time = st.session_state.login_time
        duration = (logout_time - login_time).total_seconds() / 3600

        session_df = pd.DataFrame([{
            "User": st.session_state.username,
            "Login Time": login_time,
            "Logout Time": logout_time,
            "Hours": round(duration, 2)
        }])

        if os.path.exists(SESSION_LOG_PATH):
            session_df.to_csv(SESSION_LOG_PATH, mode="a", header=False, index=False)
        else:
            session_df.to_csv(SESSION_LOG_PATH, index=False)

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.login_time = None
        st.success("Logged out successfully!")

# Login Page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login(username, password)
        if user is not None:
            st.success(f"Welcome {user['Emp Name']}!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# Form Page
def form_page(user_info):
    st.title("Form Submission")
    emp_id = user_info["Emp ID"]
    emp_name = user_info["Emp Name"]
    project = user_info["Project"]
    category = user_info["Project Category"]

    with st.form("data_form"):
        st.write("**Auto-filled Information**")
        st.text_input("Emp ID", emp_id, disabled=True)
        st.text_input("Emp Name", emp_name, disabled=True)
        st.text_input("Project", project, disabled=True)
        st.text_input("Project Category", category, disabled=True)

        st.write("**Fill Your Production Details**")
        chart_id = st.text_input("Chart ID")
        page_no = st.number_input("Page No", min_value=0)
        dos = st.number_input("No of DOS", min_value=0)
        codes = st.number_input("No of Codes", min_value=0)
        error_type = st.selectbox("Error Type", ["None", "Minor", "Major", "Critical"])
        error_comments = st.text_area("Error Comments")

        submit = st.form_submit_button("Submit")
        if submit:
            new_data = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Emp ID": emp_id,
                "Emp Name": emp_name,
                "Project": project,
                "Project Category": category,
                "Chart ID": chart_id,
                "Page No": page_no,
                "No of DOS": dos,
                "No of Codes": codes,
                "Error Type": error_type,
                "Error Comments": error_comments
            }])
            if os.path.exists(DATA_FILE):
                new_data.to_csv(DATA_FILE, mode="a", header=False, index=False)
            else:
                new_data.to_csv(DATA_FILE, index=False)
            st.success("Data submitted successfully!")

            user_data = pd.read_csv(DATA_FILE)
            user_data = user_data[user_data["Emp ID"] == emp_id]
            st.download_button(
                label="📥 Download Your Submitted Data",
                data=user_data.to_csv(index=False),
                file_name=f"{emp_name}_submitted_data.csv",
                mime="text/csv"
            )

            st.subheader("📊 Filter Your Submitted Data")
            user_data["Date"] = pd.to_datetime(user_data["Date"])
            start_date = st.date_input("Start Date", user_data["Date"].min().date())
            end_date = st.date_input("End Date", user_data["Date"].max().date())
            mask = (user_data["Date"] >= pd.to_datetime(start_date)) & (user_data["Date"] <= pd.to_datetime(end_date))
            filtered_data = user_data[mask]
            st.dataframe(filtered_data)

# Dashboard Page
def dashboard_page():
    st.title("Dashboard")
    if not os.path.exists("login_sessions.csv"):
        st.warning("No session logs found.")
        return

    logs = pd.read_csv("login_sessions.csv", parse_dates=["Login Time", "Logout Time"])
    user_logs = logs[logs["User"] == st.session_state.username]

    st.metric("Total Logins", len(user_logs))
    total_seconds = round(user_logs["Hours"].sum() * 3600)
    cumulative_time = str(timedelta(seconds=total_seconds))
    st.metric("Total Time Logged In", cumulative_time)
    st.dataframe(user_logs)

# Main
if not st.session_state.logged_in:
    login_page()
else:
    menu = st.sidebar.selectbox("Menu", ["Form", "Dashboard", "Logout"])
    if menu == "Form":
        df = pd.read_csv(LOGIN_CSV)
        user_info = df[df["User Name"] == st.session_state.username].iloc[0]
        form_page(user_info)
    elif menu == "Dashboard":
        dashboard_page()
    elif menu == "Logout":
        logout()
        st.experimental_rerun()
