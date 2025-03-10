import streamlit as st
import pyodbc

# Load Database Credentials from Streamlit Secrets
if "DB" not in st.secrets:
    st.error("❌ Database credentials are missing! Please set them in Streamlit Secrets.")
    st.stop()

DB_CREDENTIALS = st.secrets["DB"]

DB_DRIVER = DB_CREDENTIALS["driver"]
DB_SERVER = DB_CREDENTIALS["server"]
DB_PORT = DB_CREDENTIALS.get("port", "3306")  # Default port is 3306
DB_DATABASE = DB_CREDENTIALS["database"]
DB_USER = DB_CREDENTIALS["user"]
DB_PASSWORD = DB_CREDENTIALS["password"]

# Connection String for ODBC
conn_str = f"""
    DRIVER={DB_DRIVER};
    SERVER={DB_SERVER};
    PORT={DB_PORT};
    DATABASE={DB_DATABASE};
    USER={DB_USER};
    PASSWORD={DB_PASSWORD};
    OPTION=3;
"""

# Streamlit UI
st.title("Database Connection Test")

def test_connection():
    try:
        with st.spinner("🔄 Connecting to the database..."):
            conn = pyodbc.connect(conn_str, timeout=10)  # 10-sec timeout
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            result = cursor.fetchone()

            if result:
                st.success(f"✅ Connected successfully to database: {result[0]}")
            else:
                st.warning("⚠️ Connection successful, but no database selected.")

            cursor.close()
            conn.close()
            st.info("🔒 Connection closed successfully.")

    except pyodbc.Error as e:
        st.error(f"❌ Database connection error: {e}")

if st.button("Test Database Connection"):
    test_connection()
