import pyodbc

# Define your connection parameters
conn_str = (
    "DRIVER={MySQL ODBC 8.0 ANSI Driver};"
    "SERVER=192.168.15.197;"  # Hostname or IP
    "PORT=3306;"  # Explicitly define the port
    "DATABASE=bcrm;"
    "USER=jborromeo;"  # Use "USER" instead of "UID"
    "PASSWORD=$PMadrid1234jb;"  # Use "PASSWORD" instead of "PWD"
    "OPTION=3;"  # Enables some compatibility options
)

try:
    print("🔄 Attempting to connect to the database...")  # Log start

    # Attempt to establish a connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Execute a simple query
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()
    
    # Print the result if connected
    if result:
        print(f"✅ Connected successfully to database: {result[0]}")
    else:
        print("⚠️ Connection successful, but no database selected.")

    # Close the connection
    cursor.close()
    conn.close()
    print("🔒 Connection closed successfully.")

except Exception as e:
    print(f"❌ Database connection error: {e}")
