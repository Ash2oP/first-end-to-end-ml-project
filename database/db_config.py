from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

def db_connect():
    try:
        conn = psycopg2.connect(
                host = os.getenv('DB_HOST'),
                port = os.getenv('DB_PORT'),
                database = os.getenv('DB_NAME'),
                user = os.getenv('DB_USER'),
                password = os.getenv('DB_PASSWORD')
            )
        print("Database connected successfully")
        return conn
    except Exception as e:
        print(f"Database not connected.\nError : {e}")
        return None
    
if __name__ == "__main__":
    conn = db_connect()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT version()")
        
        db_ver = cur.fetchone()
        print(f"Connected to : {db_ver[0]}")
        
        cur.close()
        conn.close()
        print("Connection Closed")