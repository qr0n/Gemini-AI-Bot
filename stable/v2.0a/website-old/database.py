import mysql.connector
from mysql.connector import Error
from config import Config

db = mysql.connector.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASS,
    database=Config.DB_NAME,
)


class Database:

    @staticmethod
    def list_nuggets():
        if not db:
            return []

        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT name, avatar_url FROM bots")
            return cursor.fetchall()
        except Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def get_db():
        try:
            if not db.is_connected():
                db.reconnect()
            return db
        except Error as e:
            print(f"Database connection error: {e}")
            return None
