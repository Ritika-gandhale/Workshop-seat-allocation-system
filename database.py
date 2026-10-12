import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",
            database="workshop_db"
        )
        return connection

    except Error as e:
        print("Database connection failed:", e)
        return None