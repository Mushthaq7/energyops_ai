import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "energyops_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_SERVER", "127.0.0.1"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    print("Connected successfully!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
