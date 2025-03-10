import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
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
    /* Set background to pure white */
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
        background-color: white !important; /* Ensure white background */
        filter: none !important; /* Remove blur */
        backdrop-filter: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Dynamic Animated Text (Runs only while Streamlit app is running)
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



# Function to run the Excel macro in Python 3.12+
def run_excel_macro():
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        # REMOVE: excel.Visible = False  # No need to set visibility (causes errors in Python 3.12)

        wb = excel.Workbooks.Open(r"\\192.168.15.241\admin\ACTIVE\jlborromeo\CBS HOME LOAN\CBS HEADER MAPPING V2.xlsm")
        
        # Wait for Excel to open properly
        time.sleep(3)
        
        # Run the macro
        excel.Application.Run("AlignDataBasedOnMappingWithMissingHeaders")

        # Save & Close
        wb.Save()
        wb.Close()
        excel.Quit()
        
        st.success("✅ Macro executed successfully!")
        time.sleep(10)
        return True
    except Exception as e:
        st.error(f"❌ Failed to run macro: {e}")
        return False

# Function to run the external Python script
def run_python_script():
    try:
        script_path = r"importing\import.py"

        # Run the script
        subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)

        # Show success message
        success_message = st.empty()
        success_message.success("Python Import Script Executed Successfully! ✅")

        # Hide message after 3 seconds
        time.sleep(30)
        success_message.empty()

        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Importing Error! ❌\n{e.stderr}")  # Show error details
        return False

# Load Database Credentials
if "DB" not in st.secrets:
    st.error("❌ Database credentials missing! Set them in Streamlit Secrets.")
    st.stop()

DB_DRIVER = st.secrets["DB"].get("DRIVER", "")
DB_SERVER = st.secrets["DB"].get("SERVER", "")
DB_DATABASE = st.secrets["DB"].get("DATABASE", "")
DB_USER = st.secrets["DB"].get("UID", "")
DB_PASSWORD = st.secrets["DB"].get("PWD", "")

# Validate Secrets
if not all([DB_DRIVER, DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD]):
    st.error("❌ One or more database credentials are missing!")
    st.stop()
    
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the relative path for the queries folder in GitHub repo
QUERIES_PATH = os.path.join(BASE_DIR, "queries")

# Define the report queries dynamically
REPORT_QUERIES = {
    "MASTERLIST": os.path.join(QUERIES_PATH, "masterlist.sql"),
    "SKIPS AND COLLECT REPORT": os.path.join(QUERIES_PATH, "skips_and_collect_report.sql"),
    "COLLECT REPORT": os.path.join(QUERIES_PATH, "collect_report.sql"),
}

# Function to read an SQL query from a file
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

# Function to fetch data from ODBC database (Masterlist + Reports)
def load_data(report_type):
    query = load_query(report_type)
    if not query:
        return pd.DataFrame()

    try:
        conn = pyodbc.connect(
            f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USER};PWD={DB_PASSWORD}",
            autocommit=True
        )
        with conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()


        
# Function to convert DataFrame to Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    return output.getvalue()

# Sidebar Navigation
campaigns = ["CBS HOMELOAN", "PNB HOMELOAN", "SBF HOMELOAN", "BDO HOMELOAN", "OPTION 5"]
selected_campaign = st.sidebar.selectbox("Choose a campaign:", campaigns)


# Update page title
st.title(f"{selected_campaign}")

# CBS HOMELOAN - SHOW MASTERLIST + PROCESS ENDORSEMENT
if selected_campaign == "CBS HOMELOAN":
    df_masterlist = load_data("MASTERLIST")
    
    if not df_masterlist.empty:
        st.write("---")  # Add a separator
        
        st.write("### 📊 Dashboard Metrics")
        # Ensure page config is only set once in main script, not here

        def load_data(query):
            try:
                conn = pyodbc.connect("DSN=data;UID=jborromeo;PWD=$PMadrid1234jb", autocommit=True)
                df = pd.read_sql(query, conn)
                conn.close()
                return df
            except Exception as e:
                st.error(f"Database connection error: {e}")
                return pd.DataFrame()

        def get_active_accounts():
            query = """
            SELECT COUNT(DISTINCT leads.leads_chcode) AS active_accounts
            FROM bcrm.leads
            WHERE leads.leads_client_id = 191 AND leads.leads_users_id <> 659;
            """
            df = load_data(query)
            return df.iloc[0, 0] if not df.empty else 0

        def get_ptp_count():
            query = """
            SELECT COUNT(DISTINCT leads.leads_acctno) AS ptp_count
            FROM bcrm.leads_result
            INNER JOIN bcrm.leads ON leads_result.leads_result_lead = leads.leads_id
            INNER JOIN bcrm.leads_status ON leads_result.leads_result_status_id = leads_status.leads_status_id
            WHERE leads.leads_client_id = 191 AND leads_status.leads_status_name = 'PTP' 
            AND leads.leads_users_id <> 659;
            """
            df = load_data(query)
            return df.iloc[0, 0] if not df.empty else 0

        def get_payment_count():
            query = """
            SELECT COUNT(DISTINCT leads.leads_acctno) AS ptp_count
            FROM bcrm.leads_result
            INNER JOIN bcrm.leads ON leads_result.leads_result_lead = leads.leads_id
            INNER JOIN bcrm.leads_status ON leads_result.leads_result_status_id = leads_status.leads_status_id
            WHERE leads.leads_client_id = 191 AND leads_status.leads_status_name = 'PAYMENT' 
            AND leads.leads_users_id <> 659;
            """
            df = load_data(query)
            return df.iloc[0, 0] if not df.empty else 0

        def get_active_accounts_trend():
            query = """
            SELECT DATE(leads.leads_endo_date) AS date, COUNT(DISTINCT leads.leads_chcode) AS active_accounts
            FROM bcrm.leads
            WHERE leads.leads_client_id = 191 AND leads.leads_users_id <> 659
            GROUP BY DATE(leads.leads_ts)
            ORDER BY DATE(leads.leads_ts);
            """
            return load_data(query)

        st.title("Dashboard - Active Accounts & PTP Count")

        col1, col2, col3 = st.columns(3)

        with col1:
            active_accounts = get_active_accounts()
            st.markdown(f'<div class="metric-box">Active Accounts: {active_accounts}</div>', unsafe_allow_html=True)

        with col2:
            ptp_count = get_ptp_count()
            st.markdown(f'<div class="metric-box">PTP Count: {ptp_count}</div>', unsafe_allow_html=True)

        with col3:
            payment_count = get_payment_count()
            st.markdown(f'<div class="metric-box">Payment Count: {payment_count}</div>', unsafe_allow_html=True)

        # Line Chart for Active Accounts Trend
        df_trend = get_active_accounts_trend()
        if not df_trend.empty:
            st.write("## Active Accounts Trend")
            st.line_chart(df_trend.set_index("date"))

        st.dataframe(df_masterlist)  # Not sure why this is duplicated, you might want to remove it

        col1, col2 = st.columns([5, 0.97])

        with col1:
            if st.button("PROCESS ENDORSEMENT", use_container_width=False):
                status_placeholder = st.empty()  # Create a placeholder for dynamic updates
                status_placeholder.info("Running Excel Macro... Please wait.")
                time.sleep(5)
                status_placeholder.empty()
                # ✅ First, run the Excel macro
                if run_excel_macro():
                    status_placeholder.info("Excel Macro executed successfully. Now running Import Python Script... Please wait.")
                    time.sleep(5)

                    # ✅ Then, run the Python script
                    if run_python_script():
                        status_placeholder.info("Please wait.")
                        status_placeholder.empty()  # Clear the message
                    else:
                        status_placeholder.error("Importing Error! ❌ File not found!")
                        time.sleep(5)  # Wait for 5 seconds
                        status_placeholder.empty()  # Clear the message
                else:
                    status_placeholder.error("Failed to execute Excel Macro! ❌")
                # ✅ Clear status message after 5 seconds
                time.sleep(5)
                status_placeholder.empty()
        
        with col2:
            st.download_button(
                label="📥 DOWNLOAD MASTERLIST",
                data=convert_df_to_excel(df_masterlist),
                file_name="Masterlist.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            

# BDO HOMELOAN - Report Selection
elif selected_campaign == "BDO HOMELOAN":
    if "report_type" not in st.session_state:
        st.session_state["report_type"] = "SKIPS AND COLLECT REPORT"  # Default view

    col1, col2 = st.columns(2)
    if col1.button("SKIPS AND COLLECT REPORT", use_container_width=True):
        st.session_state["report_type"] = "SKIPS AND COLLECT REPORT"
        st.rerun()
    if col2.button("COLLECT REPORT", use_container_width=True):
        st.session_state["report_type"] = "COLLECT REPORT"
        st.rerun()

    # Load and display selected report
    report_type = st.session_state["report_type"]
    st.title(f"BDO HOMELOAN - {report_type}")

    df_option1 = load_data(report_type)

    # ✅ Display only the first 30 rows in the table
    st.dataframe(df_option1.head(30))

    # ✅ Add a "Download Report" button to export full data
    if not df_option1.empty:
        st.download_button(
            label="📥 Download Full Report",
            data=convert_df_to_excel(df_option1),
            file_name=f"{report_type.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
