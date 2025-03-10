import mysql.connector

try:
    conn = mysql.connector.connect(
        host="192.168.15.197",
        port=3306,  # <-- Add port here
        database="bcrm",
        user="jborromeo",
        password="$PMadrid1234jb"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()

    print(f"Connected successfully to database: {result[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Database connection error: {e}")
