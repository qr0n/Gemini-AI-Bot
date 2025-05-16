from functools import wraps
from flask import session, request, redirect, url_for, jsonify
import requests
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# Discord OAuth2 credentials
CLIENT_ID = "1336834527951192134"
CLIENT_SECRET = "5NA0Yh11FgHhH8o8H8yF_6AYSBgltizK"
REDIRECT_URI = "http://localhost:5000/auth/callback"
API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"
PERSONALITY_DATA_DIR = Path("data/personality_traits")
PERSONALITY_DATA_DIR.mkdir(parents=True, exist_ok=True)


db = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your username
    password="iron",  # Replace with your password
    database="bot_memory",  # Specify the database
)


class Helpers:
    def requires_auth(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Check if "token" is in the session
            if "token" not in session:
                token = request.cookies.get("token")
                if token:
                    session["token"] = token
                else:
                    return redirect(url_for("login"))
            return func(*args, **kwargs)

        return decorated_function

    def get_user_data():
        headers = {"Authorization": f"Bearer {session['token']}"}
        response = requests.get(f"{API_BASE_URL}/users/@me", headers=headers)
        user_data = response.json()
        print("User data: ", user_data)
        return user_data

    def list_nuggets():
        try:
            # Get from database
            database = Helpers.get_db()
            if not database:
                return jsonify({"error": "Database connection failed"}), 500

            cursor = database.cursor(dictionary=True)
            cursor.execute("SELECT name, alias, avatar_url FROM bots")
            traits = cursor.fetchall()
            cursor.close()

            print(traits)
            return traits
        except Error as e:
            return jsonify({"error": str(e)}), 500

    def get_db():
        try:
            if not db.is_connected():
                db.reconnect()
            return db
        except Error as e:
            print(f"Database connection error: {e}")
            return None
