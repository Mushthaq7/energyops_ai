import psycopg2

try:
    conn = psycopg2.connect(
        dbname="energyops_db",
        user="haddad",
        password="",
        host="localhost",
        port="5432"
    )
    print("Connected successfully!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
