import streamlit as st
import mysql.connector

# Load Database Credentials from Streamlit Secrets
if "DB" not in st.secrets:
    st.error("❌ Database credentials are missing! Please set them in Streamlit Secrets.")
    st.stop()

DB_CREDENTIALS = st.secrets["DB"]

DB_HOST = DB_CREDENTIALS["server"]
DB_PORT = DB_CREDENTIALS.get("port", "3306")  # Default port is 3306
DB_DATABASE = DB_CREDENTIALS["database"]
DB_USER = DB_CREDENTIALS["user"]
DB_PASSWORD = DB_CREDENTIALS["password"]

# Streamlit UI
st.title("Database Connection Test")

def test_connection():
    try:
        with st.spinner("🔄 Connecting to the database..."):
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_DATABASE,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=10  # 10-sec timeout
            )
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

    except mysql.connector.Error as e:
        st.error(f"❌ Database connection error: {e}")

if st.button("Test Database Connection"):
    test_connection()
