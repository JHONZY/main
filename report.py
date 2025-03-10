import streamlit as st
import pandas as pd
import pyodbc
import subprocess
import io
import time
import os
import sys
import runpy

# Streamlit Page Config
st.set_page_config(page_title="REPORTING WEBSITE", layout="wide")

# Custom CSS for animation
st.markdown(
    """
    <style>
    @keyframes fadeInOut {
        0% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; }
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    html, body, .stApp {
        background-color: white !important;
        color: black !important;
    }
    .center-text, .footer {
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        font-weight: bold;
        animation: fadeInOut 3s ease-in-out infinite;
    }
    .center-text {
        top: 30%;
        font-size: 120px;
        color: #4CAF50;
        background: linear-gradient(45deg, #ff0000, #ff7300, #ffeb00, #47ff00, #00ffcc, #007bff, #b300ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .footer {
        bottom: 50px;
        font-size: 16px;
        color: grey;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Dynamic Animated Text
animation_placeholder = st.empty()
footer_placeholder = st.empty()

def show_animation():
    animation_placeholder.markdown('<div class="center-text">GENESIS</div>', unsafe_allow_html=True)
    footer_placeholder.markdown('<div class="footer">powered by chester ❤️</div>', unsafe_allow_html=True)

def hide_animation():
    animation_placeholder.empty()
    footer_placeholder.empty()

show_animation()
time.sleep(3)  # Display animation for 3 seconds
hide_animation()

# Load Database Credentials
if "DB" not in st.secrets:
    st.error("❌ Database credentials missing! Set them in Streamlit Secrets.")
    st.stop()

DB_SERVER = st.secrets["DB"]["server"]
DB_USER = st.secrets["DB"]["user"]
DB_PASSWORD = st.secrets["DB"]["password"]
DB_NAME = st.secrets["DB"]["database"]
DB_DRIVER = st.secrets["DB"]["driver"]

# Validate Secrets
if not all([DB_DRIVER, DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD]):
    st.error("❌ One or more database credentials are missing!")
    st.stop()

# Excel Macro Execution
def run_excel_macro():
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        wb = excel.Workbooks.Open(r"\\192.168.15.241\admin\ACTIVE\jlborromeo\CBS HOME LOAN\CBS HEADER MAPPING V2.xlsm")
        
        time.sleep(3)  # Ensure Excel is ready
        excel.Application.Run("AlignDataBasedOnMappingWithMissingHeaders")
        wb.Save()
        wb.Close()
        excel.Quit()

        st.success("✅ Macro executed successfully!")
        time.sleep(3)
        return True
    except Exception as e:
        st.error(f"❌ Failed to run macro: {e}")
        return False

# Run External Python Script
def run_python_script():
    try:
        script_path = r"importing/import.py"
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)

        st.success("✅ Python Import Script Executed Successfully!")
        time.sleep(3)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Importing Error:\n{e.stderr}")
        return False

# Load SQL Queries
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUERIES_PATH = os.path.join(BASE_DIR, "queries")

REPORT_QUERIES = {
    "MASTERLIST": os.path.join(QUERIES_PATH, "masterlist.sql"),
    "SKIPS AND COLLECT REPORT": os.path.join(QUERIES_PATH, "skips_and_collect_report.sql"),
    "COLLECT REPORT": os.path.join(QUERIES_PATH, "collect_report.sql"),
}

def load_query(report_type):
    file_path = REPORT_QUERIES.get(report_type)
    if not file_path:
        st.error(f"Invalid report type: {report_type}")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading SQL query file: {file_path}\nError: {e}")
        return None

# Fetch Data from Database
def load_data(report_type):
    query = load_query(report_type)
    if not query:
        return pd.DataFrame()

    try:
        conn = pyodbc.connect(
            f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}",
            autocommit=True
        )
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except pyodbc.Error as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()

# Convert DataFrame to Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    return output.getvalue()

# Sidebar Navigation
campaigns = ["CBS HOMELOAN", "PNB HOMELOAN", "SBF HOMELOAN", "BDO HOMELOAN"]
selected_campaign = st.sidebar.selectbox("Choose a campaign:", campaigns)

st.title(selected_campaign)

if selected_campaign == "CBS HOMELOAN":
    df_masterlist = load_data("MASTERLIST")
    st.dataframe(df_masterlist)

    if st.button("PROCESS ENDORSEMENT"):
        status_placeholder = st.empty()
        status_placeholder.info("Running Excel Macro... Please wait.")
        time.sleep(3)

        if run_excel_macro():
            status_placeholder.info("Now running Import Python Script... Please wait.")
            time.sleep(3)

            if run_python_script():
                status_placeholder.success("Process Completed Successfully! ✅")
            else:
                status_placeholder.error("❌ Importing Error! File not found.")
        else:
            status_placeholder.error("❌ Failed to execute Excel Macro!")

    st.download_button(
        label="📥 DOWNLOAD MASTERLIST",
        data=convert_df_to_excel(df_masterlist),
        file_name="Masterlist.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif selected_campaign == "BDO HOMELOAN":
    report_type = st.radio("Choose Report", ["SKIPS AND COLLECT REPORT", "COLLECT REPORT"])
    df_report = load_data(report_type)
    st.dataframe(df_report.head(30))

    st.download_button(
        label="📥 Download Full Report",
        data=convert_df_to_excel(df_report),
        file_name=f"{report_type.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
