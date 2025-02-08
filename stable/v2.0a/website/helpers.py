from functools import wraps
from flask import session, request, redirect, url_for
import requests

# Discord OAuth2 credentials
CLIENT_ID = "1336834527951192134"
CLIENT_SECRET = "5NA0Yh11FgHhH8o8H8yF_6AYSBgltizK"
REDIRECT_URI = "http://localhost:5000/callback"
API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"


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
