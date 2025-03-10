import streamlit as st
import mysql.connector

# Load credentials securely
DB_CREDENTIALS = st.secrets["DB"]

try:
    conn = mysql.connector.connect(
        host=DB_CREDENTIALS["host"],
        database=DB_CREDENTIALS["database"],
        user=DB_CREDENTIALS["user"],
        password=DB_CREDENTIALS["password"]
    )

    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()
    
    st.success(f"✅ Connected successfully to database: {result[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    st.error(f"❌ Database connection error: {e}")
