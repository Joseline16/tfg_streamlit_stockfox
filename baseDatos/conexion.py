
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# conectar la base de datos

def get_connection():
    try:
        conn =psycopg2.connect(
        host=os.getenv("PGHOST"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        port=os.getenv("PGPORT")
     )
        return conn
    except Exception as e:
       print("Error al conectar a la base de datos:", e)
    return None 


